# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "tree-sitter>=0.25,<0.27",
#   "tree-sitter-java>=0.23,<0.24",
# ]
# ///
"""從入口類別出發,解析 Java 原始碼,輸出類別與類別之間的關係。

從 --entry 指定的類別開始,沿著它相依的類別一層一層往下走(同一層照名稱排序),
收滿 --max-classes 個就停。只收 --root 底下有原始碼的類別;JDK 與第三方的型別
只會出現在方法簽章的文字裡。

stdout 是一份 JSON:
  entry         入口類別的全名
  truncated     是否因為 --max-classes 而沒有走完
  not_expanded  碰到但沒有收進來的類別
  classes       每個類別的 name、kind、file 與 public 方法
  relations     類別之間的關係,type 是 繼承、實作、關聯(欄位持有)、相依(其餘用到)
"""
import argparse
import difflib
import json
import os
import sys
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path

import tree_sitter_java
from tree_sitter import Language, Parser

KINDS = {
    "class_declaration": "class",
    "interface_declaration": "interface",
    "enum_declaration": "enum",
    "record_declaration": "record",
    "annotation_type_declaration": "annotation",
}
# 角色依強到弱排列;同一個對象已有較強的關係時,不再輸出「相依」
ROLES = {"extends": "繼承", "implements": "實作", "field": "關聯", "dep": "相依"}
CLAUSE_ROLES = {
    "superclass": "extends",
    "extends_interfaces": "extends",
    "super_interfaces": "implements",
}
SKIPPED_DIRS = {"node_modules"}


@dataclass
class TypeInfo:
    id: str  # 套件名 + 外層類別 + 自己,例如 com.example.Outer.Inner
    display: str  # 不含套件名,例如 Outer.Inner
    kind: str
    file: str
    package: str
    enclosing: list[str]  # 自己與外層類別的 id,由內而外
    single_imports: dict[str, str]
    wildcard_imports: list[str]
    methods: list[str] = field(default_factory=list)
    refs: dict[str, set[str]] = field(default_factory=lambda: {role: set() for role in ROLES})


def text(node) -> str:
    return " ".join(node.text.decode("utf-8", errors="replace").split())


def modifiers(node) -> set[str]:
    for child in node.children:
        if child.type == "modifiers":
            return {token.type for token in child.children}
    return set()


def members(body):
    """類別本體的直屬成員;enum 的成員包在 enum_body_declarations 裡,攤開來。"""
    if body is None:
        return
    for child in body.named_children:
        if child.type == "enum_body_declarations":
            yield from child.named_children
        else:
            yield child


def signature(method) -> str:
    """寫成類別圖用的 `+<方法名>(<型別> <參數名>, ...) <回傳型別>`;void 不寫回傳型別。"""
    params = []
    for param in method.child_by_field_name("parameters").named_children:
        if param.type == "formal_parameter":
            dims = param.child_by_field_name("dimensions")
            type_text = text(param.child_by_field_name("type")) + (text(dims) if dims else "")
            params.append(f"{type_text} {text(param.child_by_field_name('name'))}")
        elif param.type == "spread_parameter":
            type_node = next(c for c in param.named_children if c.type != "modifiers")
            name_node = param.named_children[-1].child_by_field_name("name")
            params.append(f"{text(type_node)}... {text(name_node)}")
    result = f"+{text(method.child_by_field_name('name'))}({', '.join(params)})"
    returns = method.child_by_field_name("type")
    if returns.type != "void_type":
        dims = method.child_by_field_name("dimensions")
        result += f" {text(returns)}{text(dims) if dims else ''}"
    return result


def collect(root, role: str, refs: dict[str, set[str]], type_params: set[str], skip: set[int]) -> None:
    """把 root 底下寫到的型別名稱依角色收進 refs;skip 是要略過的節點(另外處理的巢狀類別)。"""
    stack = [(root, role)]
    while stack:
        node, role = stack.pop()
        kind = node.type
        if node.id in skip:
            continue
        if kind in ("type_identifier", "scoped_type_identifier"):
            name = "".join(text(node).split())
            if "<" not in name and "@" not in name:
                refs[role].add(name)
                continue
        elif kind == "type_parameter":
            # 第一個 type_identifier 是型別參數自己的名字(例如 T),不是用到的型別
            named = False
            for child in node.children:
                if child.type == "type_identifier" and not named:
                    type_params.add(text(child))
                    named = True
                else:
                    stack.append((child, "dep"))
            continue
        elif kind in CLAUSE_ROLES:
            role = CLAUSE_ROLES[kind]
        elif kind == "type_arguments" and role in ("extends", "implements"):
            role = "dep"  # `extends Base<Foo>` 繼承的是 Base,Foo 只是被用到
        elif kind in ("method_invocation", "field_access"):
            # `Foo.bar()`、`Foo.CONST`:大寫開頭的當成型別名稱,解析不到專案內的類別就會被丟掉
            target = node.child_by_field_name("object")
            if target is not None and target.type == "identifier" and text(target)[:1].isupper():
                refs["dep"].add(text(target))
        elif kind == "method_reference":
            target = node.children[0]
            if target.type == "identifier" and text(target)[:1].isupper():
                refs["dep"].add(text(target))
        elif kind in ("annotation", "marker_annotation"):
            refs["dep"].add("".join(text(node.child_by_field_name("name")).split()))
        stack.extend((child, role) for child in node.children)


class Project:
    def __init__(self, root: Path):
        self.root = root
        self.parser = Parser(Language(tree_sitter_java.language()))
        self.types: dict[str, TypeInfo] = {}
        self.parsed: set[Path] = set()
        self.relations_cache: dict[str, dict[str, list[str]]] = {}
        # 檔名(不含 .java)→ 相對於 root 的路徑;只列目錄,不讀檔
        self.index: dict[str, list[Path]] = {}
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d not in SKIPPED_DIRS)
            for filename in sorted(filenames):
                if filename.endswith(".java"):
                    relative = Path(dirpath).relative_to(root) / filename
                    self.index.setdefault(relative.stem, []).append(relative)

    def parse(self, relative: Path) -> None:
        if relative in self.parsed:
            return
        self.parsed.add(relative)
        path = self.root / relative
        tree = self.parser.parse(path.read_bytes())
        if tree.root_node.has_error:
            print(f"警告: {path.as_posix()} 有語法錯誤,這個檔的結果可能不完整。", file=sys.stderr)
        package, single_imports, wildcard_imports = "", {}, []
        for child in tree.root_node.named_children:
            if child.type == "package_declaration":
                package = "".join(text(child.named_children[-1]).split())
            elif child.type == "import_declaration":
                tokens = {token.type for token in child.children}
                if "static" in tokens:
                    continue
                name = "".join(text(next(c for c in child.named_children if c.type != "asterisk")).split())
                if "asterisk" in tokens:
                    wildcard_imports.append(name)
                else:
                    single_imports[name.rsplit(".", 1)[-1]] = name
        for child in tree.root_node.named_children:
            if child.type in KINDS:
                self.declare(child, path.as_posix(), package, single_imports, wildcard_imports, None, set())

    def declare(self, node, file, package, single_imports, wildcard_imports, outer, outer_type_params) -> None:
        name = text(node.child_by_field_name("name"))
        display = f"{outer.display}.{name}" if outer else name
        type_id = f"{package}.{display}" if package else display
        if type_id in self.types:
            print(f"警告: {type_id} 在 {self.types[type_id].file} 與 {file} 各有一份,採用前者。", file=sys.stderr)
            return
        kind = KINDS[node.type]
        if kind == "class" and "abstract" in modifiers(node):
            kind = "abstract class"
        info = TypeInfo(
            id=type_id,
            display=display,
            kind=kind,
            file=file,
            package=package,
            enclosing=[type_id] + (outer.enclosing if outer else []),
            single_imports=single_imports,
            wildcard_imports=wildcard_imports,
        )
        self.types[type_id] = info

        body = node.child_by_field_name("body")
        body_members = list(members(body))
        nested = [member for member in body_members if member.type in KINDS]
        skip = {member.id for member in nested}
        type_params = set(outer_type_params)
        record_components = node.child_by_field_name("parameters") if kind == "record" else None

        for child in node.children:
            if body is not None and child.id == body.id:
                continue
            is_components = record_components is not None and child.id == record_components.id
            collect(child, "field" if is_components else "dep", info.refs, type_params, skip)
        for member in body_members:
            if member.id in skip:
                continue
            if member.type == "field_declaration":
                field_type = member.child_by_field_name("type")
                for child in member.children:
                    collect(child, "field" if child.id == field_type.id else "dep", info.refs, type_params, skip)
                continue
            collect(member, "dep", info.refs, type_params, skip)
            if member.type == "method_declaration":
                tokens = modifiers(member)
                # interface 的方法沒寫 private 就是 public
                if "private" not in tokens if kind in ("interface", "annotation") else "public" in tokens:
                    info.methods.append(signature(member))
        for role in info.refs:
            info.refs[role] -= type_params

        for member in nested:
            self.declare(member, file, package, single_imports, wildcard_imports, info, type_params)

    def lookup(self, dotted: str) -> str | None:
        """把全名對到專案內的類別;需要時才去解析檔名與套件路徑都對得上的檔。"""
        if dotted in self.types:
            return dotted
        parts = dotted.split(".")
        for split in range(len(parts), 0, -1):
            package_parts, stem = tuple(parts[: split - 1]), parts[split - 1]
            for relative in self.index.get(stem, ()):
                directory = relative.parent.parts
                if not package_parts or directory[-len(package_parts):] == package_parts:
                    self.parse(relative)
            if dotted in self.types:
                return dotted
        return None

    def resolve(self, name: str, info: TypeInfo) -> str | None:
        """把 info 這個類別裡寫到的型別名稱對到專案內的類別;對不到(JDK、第三方)回 None。"""
        head, *rest = name.split(".")
        base = next((f"{outer}.{head}" for outer in info.enclosing if f"{outer}.{head}" in self.types), None)
        if base is None and head in info.single_imports:
            base = self.lookup(info.single_imports[head])
            if base is None:
                return None
        if base is None:
            base = self.lookup(f"{info.package}.{head}" if info.package else head)
        if base is None:
            base = next((found for pkg in info.wildcard_imports if (found := self.lookup(f"{pkg}.{head}"))), None)
        if base is None:
            return self.lookup(name) if rest else None
        for segment in rest:
            if f"{base}.{segment}" not in self.types:
                break
            base = f"{base}.{segment}"
        return base

    def relations(self, type_id: str) -> dict[str, list[str]]:
        """type_id 相依的每個專案內類別 → 關係種類。"""
        if type_id not in self.relations_cache:
            info = self.types[type_id]
            found: dict[str, list[str]] = {}
            for role, relation in ROLES.items():
                for name in sorted(info.refs[role]):
                    target = self.resolve(name, info)
                    if target is None or target == type_id:
                        continue
                    kinds = found.setdefault(target, [])
                    if relation not in kinds and not (relation == "相依" and kinds):
                        kinds.append(relation)
            self.relations_cache[type_id] = found
        return self.relations_cache[type_id]

    def find_entry(self, entry: str) -> list[str]:
        exact = self.lookup(entry)
        for relative in self.index.get(entry.split(".")[0], ()):
            self.parse(relative)
        matches = {info.id for info in self.types.values() if info.display == entry}
        if exact:
            matches.add(exact)
        return sorted(matches)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", required=True, type=Path, help="專案的根目錄;在它底下找 .java 檔")
    parser.add_argument(
        "--entry",
        required=True,
        help="入口類別,從它開始往下走;給簡名(Router)或含套件的全名(com.example.Router),巢狀類別寫 Outer.Inner",
    )
    parser.add_argument("--max-classes", type=int, default=30, help="最多輸出幾個類別(含入口類別),預設 30")
    args = parser.parse_args()
    if args.max_classes < 1:
        parser.error(f"--max-classes 收到 {args.max_classes},要給 1 以上的整數")
    if not args.root.is_dir():
        print(f"錯誤: {args.root} 不是目錄。--root 要給專案的根目錄。", file=sys.stderr)
        sys.exit(1)

    project = Project(args.root)
    if not project.index:
        print(f"錯誤: {args.root} 底下沒有 .java 檔。這支腳本目前只支援 Java;--root 要給含有 Java 原始碼的目錄。", file=sys.stderr)
        sys.exit(1)

    matches = project.find_entry(args.entry)
    if not matches:
        close = difflib.get_close_matches(args.entry.rsplit(".", 1)[-1], sorted(project.index), n=5)
        hint = f";名稱相近的有: {', '.join(close)}" if close else ""
        print(
            f"錯誤: 在 {args.root} 底下找不到類別 {args.entry}。"
            f"--entry 要給類別的簡名(Router)或含套件的全名(com.example.Router){hint}。",
            file=sys.stderr,
        )
        sys.exit(1)
    if len(matches) > 1:
        print(
            f"錯誤: {args.entry} 對應到 {len(matches)} 個類別: {', '.join(matches)}。--entry 請改給其中一個全名。",
            file=sys.stderr,
        )
        sys.exit(1)

    entry = matches[0]
    included, seen, not_expanded = [entry], {entry}, set()
    queue = deque([entry])
    while queue:
        current = queue.popleft()
        for target in sorted(project.relations(current), key=lambda t: (project.types[t].display, t)):
            if target in seen:
                continue
            if len(included) < args.max_classes:
                seen.add(target)
                included.append(target)
                queue.append(target)
            else:
                not_expanded.add(target)

    # 簡名撞名時改用全名,讓 relations 的 from / to 指得到唯一的類別
    shown = included + sorted(not_expanded)
    counts = Counter(project.types[type_id].display for type_id in shown)
    label = {
        type_id: project.types[type_id].display if counts[project.types[type_id].display] == 1 else type_id
        for type_id in shown
    }
    classes = [
        {
            "name": label[type_id],
            "kind": project.types[type_id].kind,
            "file": project.types[type_id].file,
            "methods": project.types[type_id].methods,
        }
        for type_id in included
    ]
    relations = [
        {"from": label[type_id], "to": label[target], "type": relation}
        for type_id in included
        for target, kinds in sorted(project.relations(type_id).items(), key=lambda item: label.get(item[0], ""))
        if target in seen
        for relation in kinds
    ]

    # 一個類別、一條關係各佔一行:比整份縮排省字,又比擠成一行好讀
    def dump(value) -> str:
        return json.dumps(value, ensure_ascii=False)

    def dump_list(items) -> str:
        return "[\n" + ",\n".join(f"    {dump(item)}" for item in items) + "\n  ]" if items else "[]"

    print(
        "{\n"
        f'  "entry": {dump(entry)},\n'
        f'  "truncated": {dump(bool(not_expanded))},\n'
        f'  "not_expanded": {dump([label[type_id] for type_id in sorted(not_expanded, key=label.get)])},\n'
        f'  "classes": {dump_list(classes)},\n'
        f'  "relations": {dump_list(relations)}\n'
        "}"
    )
    print(
        f"解析了 {len(project.parsed)} 個檔(專案共 {sum(len(paths) for paths in project.index.values())} 個 .java),"
        f"輸出 {len(included)} 個類別、{len(relations)} 條關係。",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
