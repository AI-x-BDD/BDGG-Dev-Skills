# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""檢查一份 tasks.md 的錨點與介面覆蓋。

檢查項目:
  任務編號      T 編號從 T001 起連號、不重複;一個編號可以拆成帶小寫字尾的子任務(T003a、T003b,跨 repo 各一個),
                字尾從 a 起連續,拆了就不再同時寫不帶字尾的同號任務
  錨點          每個 ⚙ 與 📎 的引用都寫成 `檔案` § 錨點,不只寫檔名
  ⚙ 錨點存在    ⚙ 指到的規格檔在 spec package 裡,錨點(operation、path、schema、Table、data-state、#id、.class、
                services、location、Dockerfile 指令、CSS)在那個檔裡找得到;`§ 全檔` 代表整個檔
  📎 編號存在   📎 引用 spec.md 的 FR / NFR / SC、research.md 的 R、plan.md 的 Q 時,這些編號在那份文件裡找得到
  介面覆蓋      規格檔裡必須覆蓋的每個介面元素(與 list_elements.py 的 required 相同)都出現在某一張介面覆蓋表,
                那一列的實作欄與測試欄都有任務,表上的任務都存在,而且它的 ⚙ 列了那一列的元素
                (AsyncAPI operation 的訊息 payload 指到的 schema 也算列了那個 operation)
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HTTP_METHODS = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}
DBML_TABLE = re.compile(r"^\s*Table\s+(\"[^\"]+\"|[\w.]+)", re.MULTILINE)
DBML_COLUMN = re.compile(r"^\s*(\"[^\"]+\"|\w+)\s+[\w(),.\[\]]+")
DATA_STATE = re.compile(r'data-state="([^"]+)"')
HTML_ID = re.compile(r'\bid="([^"]+)"')
HTML_CLASS = re.compile(r'\bclass="([^"]+)"')
HTML_TAG = re.compile(r"<([a-z][a-z0-9]*)\b")
CSS_AT_MEDIA = re.compile(r"(@media[^{]+?)\s*\{")
NGINX_LOCATION = re.compile(r"^\s*location\s+([^{]+?)\s*\{", re.MULTILINE)
DOCKER_INSTRUCTION = re.compile(r"^\s*([A-Z]+)\s", re.MULTILINE)

TASK_LINE = re.compile(r"^- \[[ xX]\] T(\d{3}[a-z]?)\b")
SUB_LINE = re.compile(r"^\s+- (⚙|📎) (.*)$")
REFERENCE = re.compile(r"^`([^`]+)`\s*§\s*(.+)$")
COVERAGE_HEADING = re.compile(r"^### 介面覆蓋[((](.+?)[))]")
COVERAGE_ROW = re.compile(r"^\| (`.+?) \| (.*?) \| (.*?) \|$")
TASK_ID = re.compile(r"T(\d{3}[a-z]?)(?![A-Za-z0-9])")
SPEC_ID = re.compile(r"\b((?:FR|NFR|SC)-\d{3})\b")
RESEARCH_ID = re.compile(r"\bR(\d+)\b")
PLAN_ID = re.compile(r"\bQ(\d+)\b")
OPEN = "(("
CLOSE = "))"

C_IDS = "任務編號從 T001 起連號、不重複"
C_ANCHOR = "每個 ⚙ 與 📎 的引用都寫到錨點"
C_GEAR = "⚙ 的錨點在規格檔裡找得到"
C_CLIP = "📎 的編號在依據文件裡找得到"
C_COVER = "必須覆蓋的介面元素都在介面覆蓋表上"
C_ROW = "介面覆蓋表的每一列都有存在、且 ⚙ 列了該元素的實作與測試任務"
CHECKS = [C_IDS, C_ANCHOR, C_GEAR, C_CLIP, C_COVER, C_ROW]


def next_task_ids(previous: str | None) -> list[str]:
    """回傳緊接在 previous 之後可以出現的任務編號:下一個編號(不帶字尾或從 a 起拆),或同一個編號的下一個字尾。"""
    number = int(previous[1:4]) if previous else 0
    suffix = previous[4:] if previous else ""
    allowed = []
    if suffix and suffix < "z":
        allowed.append(f"T{number:03d}{chr(ord(suffix) + 1)}")
    allowed += [f"T{number + 1:03d}", f"T{number + 1:03d}a"]
    return allowed


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"錯誤: {path} 不是 UTF-8 編碼。請把它轉存成 UTF-8 再執行。", file=sys.stderr)
        sys.exit(2)


def read_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(read_text(path))
    except yaml.YAMLError as error:
        print(f"錯誤: {path} 不是合法的 YAML:{error}。請先修好這個檔再執行。", file=sys.stderr)
        sys.exit(2)
    return data if isinstance(data, dict) else {}


def payload_schemas(node: object, document: dict, seen: set[str]) -> set[str]:
    """沿著 $ref 一路追下去,收集 operation 的訊息最後指到的 components.schemas 名稱。"""
    found: set[str] = set()
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/") and ref not in seen:
            seen.add(ref)
            parts = ref[2:].split("/")
            if parts[:2] == ["components", "schemas"] and len(parts) == 3:
                found.add(f"components.schemas.{parts[2]}")
            else:
                target: object = document
                for part in parts:
                    target = target.get(part, {}) if isinstance(target, dict) else {}
                found |= payload_schemas(target, document, seen)
        for key, value in node.items():
            if key != "$ref":
                found |= payload_schemas(value, document, seen)
    elif isinstance(node, list):
        for value in node:
            found |= payload_schemas(value, document, seen)
    return found


def collect(package: Path) -> tuple[set[tuple[str, str]], dict[str, set[str]], dict[tuple[str, str], set[str]]]:
    """回傳必須覆蓋的 (檔案, 錨點)、每個規格檔可以當錨點的字串,以及每個 operation 的訊息 schema;規則與 list_elements.py 相同。"""
    required: set[tuple[str, str]] = set()
    anchors: dict[str, set[str]] = {}
    message_schemas: dict[tuple[str, str], set[str]] = {}

    def add(path: Path, anchor: str, must_cover: bool = False) -> None:
        name = path.relative_to(package).as_posix()
        anchors.setdefault(name, set()).add(anchor)
        if must_cover:
            required.add((name, anchor))

    contracts = package / "contracts"
    for path in sorted(contracts.glob("*.asyncapi.yaml")) + sorted(contracts.glob("*.asyncapi.yml")):
        data = read_yaml(path)
        anchors.setdefault(path.relative_to(package).as_posix(), set())
        for name, operation in (data.get("operations") or {}).items():
            add(path, f"operations.{name}", True)
            schemas = payload_schemas((operation or {}).get("messages"), data, set())
            message_schemas[(path.relative_to(package).as_posix(), f"operations.{name}")] = schemas
        for name in (data.get("components") or {}).get("schemas") or {}:
            add(path, f"components.schemas.{name}")
        for name, channel in (data.get("channels") or {}).items():
            add(path, f"channels.{name}")
            if isinstance(channel, dict) and "address" in channel:
                add(path, f"channels.{name}.address")
        if "servers" in data:
            add(path, "servers")
        if isinstance(data.get("info"), dict) and "description" in data["info"]:
            add(path, "info.description")

    for path in sorted(contracts.glob("*.openapi.yaml")) + sorted(contracts.glob("*.openapi.yml")):
        data = read_yaml(path)
        anchors.setdefault(path.relative_to(package).as_posix(), set())
        for route, item in (data.get("paths") or {}).items():
            for method in item or {}:
                if method.lower() in HTTP_METHODS:
                    add(path, f"paths.{route}.{method.lower()}", True)
        for name in (data.get("components") or {}).get("schemas") or {}:
            add(path, f"components.schemas.{name}")
        if "servers" in data:
            add(path, "servers")

    for path in sorted(contracts.glob("*.dbml")):
        text = read_text(path)
        anchors.setdefault(path.relative_to(package).as_posix(), set())
        for match in DBML_TABLE.finditer(text):
            table = match.group(1).strip('"')
            add(path, f"Table {table}", True)
            body = text[match.end():].split("{", 1)[-1].split("}", 1)[0]
            for line in body.splitlines():
                column = DBML_COLUMN.match(line)
                if column and not line.strip().lower().startswith(("indexes", "note", "ref")):
                    add(path, f"Table {table}.{column.group(1).strip(chr(34))}")

    for folder in sorted(p for p in package.glob("prototype*") if p.is_dir()):
        for path in sorted(folder.glob("*.html")):
            text = read_text(path)
            anchors.setdefault(path.relative_to(package).as_posix(), set())
            for state in DATA_STATE.findall(text):
                add(path, f'[data-state="{state}"]', True)
            if DATA_STATE.search(text):
                add(path, "[data-state]")
            for element_id in HTML_ID.findall(text):
                add(path, f"#{element_id}")
            for classes in HTML_CLASS.findall(text):
                for name in classes.split():
                    add(path, f".{name}")
            for tag in HTML_TAG.findall(text):
                add(path, tag)
        for path in sorted(folder.glob("*.css")):
            text = read_text(path)
            anchors.setdefault(path.relative_to(package).as_posix(), set())
            if re.search(r":root\s*\{", text):
                add(path, ":root")
            for media in CSS_AT_MEDIA.findall(text):
                add(path, " ".join(media.split()))

    deploy = package / "deploy"
    compose_names = {"compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml"}
    for path in sorted(p for p in deploy.rglob("*") if p.name in compose_names and p.is_file()):
        anchors.setdefault(path.relative_to(package).as_posix(), set())
        for service, body in (read_yaml(path).get("services") or {}).items():
            add(path, f"services.{service}", True)
            for key in body or {}:
                add(path, f"services.{service}.{key}")
    for path in sorted(deploy.rglob("*.conf")):
        anchors.setdefault(path.relative_to(package).as_posix(), set())
        for location in NGINX_LOCATION.findall(read_text(path)):
            add(path, f"location {' '.join(location.split())}", True)
    for path in sorted(deploy.rglob("Dockerfile*")):
        anchors.setdefault(path.relative_to(package).as_posix(), set())
        for instruction in DOCKER_INSTRUCTION.findall(read_text(path)):
            add(path, instruction)
    for path in sorted(deploy.rglob(".env*")):
        anchors.setdefault(path.relative_to(package).as_posix(), set())
    return required, anchors, message_schemas


def split_references(text: str) -> list[str]:
    """以括號與反引號外的 `;` 切開一行裡的各個引用。"""
    parts, current, depth, in_code = [], "", 0, False
    for char in text:
        if char == "`":
            in_code = not in_code
        elif not in_code and char in OPEN:
            depth += 1
        elif not in_code and char in CLOSE:
            depth = max(0, depth - 1)
        if char in ";;" and not in_code and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += char
    if current.strip():
        parts.append(current.strip())
    return parts


def anchor_tokens(text: str) -> list[str]:
    """取出錨點區裡括號以外的反引號字串;括號裡的是欄位或補充說明,不當錨點。"""
    tokens, current, depth, in_code = [], "", 0, False
    for char in text:
        if char == "`":
            if in_code and depth == 0:
                tokens.append(current)
            in_code, current = not in_code, ""
        elif in_code:
            current += char
        elif char in OPEN:
            depth += 1
        elif char in CLOSE:
            depth = max(0, depth - 1)
    return tokens


def resolve_file(name: str, anchors: dict[str, set[str]], previous: str | None) -> str | None:
    """把引用裡的檔名對到 spec package 裡的檔;只寫檔名時以結尾比對,同資料夾的簡寫沿用上一個檔的資料夾。"""
    if name in anchors:
        return name
    matches = [key for key in anchors if key.endswith("/" + name)]
    if previous and "/" in previous:
        sibling = previous.rsplit("/", 1)[0] + "/" + name
        if sibling in anchors:
            return sibling
    return matches[0] if len(matches) == 1 else None


def expand(tokens: list[str], known: set[str]) -> list[tuple[str, bool]]:
    """把簡寫(`MatchStart`、`nickname-empty`)補成完整錨點;回傳 (錨點, 找不找得到)。"""
    result: list[tuple[str, bool]] = []
    previous = ""
    for token in tokens:
        candidates = [token]
        if previous.startswith('[data-state="'):
            candidates.append(f'[data-state="{token}"]')
        if "." in previous and not token.startswith(("#", ".", "[")):
            candidates.append(previous.rsplit(".", 1)[0] + "." + token)
        found = next((c for c in candidates if c in known or any(k.startswith(c + ".") for k in known)), None)
        result.append((found or token, found is not None))
        if found:
            previous = found
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tasks", required=True, type=Path, help="要檢查的 tasks.md 的路徑")
    parser.add_argument("--package", required=True, type=Path, help="spec package 的路徑(spec.md 所在的資料夾)")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not args.tasks.is_file():
        print(f"錯誤: 找不到 {args.tasks}。--tasks 要給 tasks.md 的路徑。", file=sys.stderr)
        return 2
    if not (args.package / "spec.md").is_file():
        print(f"錯誤: {args.package} 底下沒有 spec.md。--package 要給 spec.md 所在的資料夾。", file=sys.stderr)
        return 2

    required, anchors, message_schemas = collect(args.package)
    docs = {name: read_text(args.package / name) for name in ("spec.md", "research.md", "plan.md") if (args.package / name).is_file()}
    violations: dict[str, list[dict]] = {check: [] for check in CHECKS}

    def bad(check: str, line: int, text: str, reason: str) -> None:
        violations[check].append({"line": line, "text": text, "reason": reason})

    lines = read_text(args.tasks).splitlines()
    tasks: dict[str, dict] = {}
    order: list[str] = []
    current: str | None = None
    coverage: list[tuple[int, str, str, str, str]] = []
    table: str | None = None
    for number, line in enumerate(lines, start=1):
        task = TASK_LINE.match(line)
        if task:
            current = "T" + task.group(1)
            if current in tasks:
                bad(C_IDS, number, line[:60], f"{current} 重複出現")
            tasks[current] = {"line": number, "gear": set(), "whole": set()}
            order.append(current)
            continue
        heading = COVERAGE_HEADING.match(line)
        if heading:
            table = heading.group(1)
            continue
        if line.startswith("#"):
            table = None
        row = COVERAGE_ROW.match(line)
        if table and row:
            coverage.append((number, table, row.group(1), row.group(2), row.group(3)))
            continue
        sub = SUB_LINE.match(line)
        if not (sub and current):
            if not line.startswith((" ", "\t")):
                current = None if line.strip() else current
            continue
        mark, body = sub.groups()
        previous_file: str | None = None
        for reference in split_references(body):
            parsed = REFERENCE.match(reference)
            if not parsed:
                bad(C_ANCHOR, number, reference, f"{current} 的 {mark} 引用沒有寫成 `檔案` § 錨點")
                continue
            name, anchor_text = parsed.groups()
            if mark == "📎":
                doc = Path(name).name
                if doc in docs:
                    pattern = {"spec.md": SPEC_ID, "research.md": RESEARCH_ID, "plan.md": PLAN_ID}[doc]
                    for match in pattern.finditer(anchor_text):
                        found = {
                            "spec.md": lambda m: re.search(rf"\*\*{re.escape(m.group(1))}\*\*", docs[doc]),
                            "research.md": lambda m: re.search(rf"^## R{m.group(1)}\.", docs[doc], re.MULTILINE),
                            "plan.md": lambda m: re.search(rf"^\| Q{m.group(1)} \|", docs[doc], re.MULTILINE),
                        }[doc](match)
                        if not found:
                            bad(C_CLIP, number, reference, f"{current} 引用的 {match.group(0)} 在 {doc} 裡找不到")
                continue
            resolved = resolve_file(name, anchors, previous_file)
            if not resolved:
                bad(C_GEAR, number, reference, f"{current} 的 ⚙ 指到 `{name}`,spec package 裡沒有這個規格檔")
                continue
            previous_file = resolved
            if anchor_text.strip().startswith("全檔"):
                tasks[current]["whole"].add(resolved)
                continue
            tokens = anchor_tokens(anchor_text)
            if not tokens:
                bad(C_GEAR, number, reference, f"{current} 的 ⚙ 在 § 後面沒有任何用反引號標出的錨點")
            for anchor, ok in expand(tokens, anchors[resolved]):
                if ok:
                    tasks[current]["gear"].add((resolved, anchor))
                else:
                    bad(C_GEAR, number, reference, f"{current} 的 ⚙ 錨點 `{anchor}` 在 `{resolved}` 裡找不到")

    previous: str | None = None
    for index, task_id in enumerate(order, start=1):
        allowed = next_task_ids(previous)
        if task_id not in allowed:
            bad(C_IDS, tasks[task_id]["line"], task_id, f"第 {index} 個任務應該是 {' 或 '.join(allowed)},實際是 {task_id}")
            break
        previous = task_id

    def task_covers(task_id: str, elements: list[tuple[str, str]]) -> bool:
        info = tasks[task_id]
        for file, anchor in elements:
            if file in info["whole"]:
                return True
            if any(f == file and (a == anchor or a.startswith(anchor + ".") or anchor.startswith(a + ".")) for f, a in info["gear"]):
                return True
            # 合約測試列的是訊息的 schema;operation 的訊息指到這個 schema,就算列了這個 operation
            if any(f == file and a in message_schemas.get((file, anchor), set()) for f, a in info["gear"]):
                return True
        return False

    covered: set[tuple[str, str]] = set()
    for number, table_name, cell, implement, test in coverage:
        elements: list[tuple[str, str]] = []
        previous_file = None
        for reference in split_references(cell):
            parsed = REFERENCE.match(reference)
            if not parsed:
                bad(C_ROW, number, reference, f"介面覆蓋({table_name})的元素沒有寫成 `檔案` § 錨點")
                continue
            resolved = resolve_file(parsed.group(1), anchors, previous_file)
            if not resolved:
                bad(C_ROW, number, reference, f"介面覆蓋({table_name})指到 `{parsed.group(1)}`,spec package 裡沒有這個規格檔")
                continue
            previous_file = resolved
            for anchor, ok in expand(anchor_tokens(parsed.group(2)), anchors[resolved]):
                if ok:
                    elements.append((resolved, anchor))
        covered.update(elements)
        for column, cell_text in (("實作", implement), ("測試", test)):
            ids = ["T" + i for i in TASK_ID.findall(cell_text)]
            if not ids:
                bad(C_ROW, number, cell[:60], f"介面覆蓋({table_name})這一列的{column}欄沒有任務")
            for task_id in ids:
                if task_id not in tasks:
                    bad(C_ROW, number, cell[:60], f"介面覆蓋({table_name})的{column}欄寫了 {task_id},但沒有這個任務")
                elif elements and not task_covers(task_id, elements):
                    bad(C_ROW, number, cell[:60], f"介面覆蓋({table_name})的{column}欄寫了 {task_id},但它的 ⚙ 沒有列這一列的任何元素")

    for file, anchor in sorted(required - covered):
        bad(C_COVER, 0, f"{file} § {anchor}", "這個介面元素沒有出現在任何一張介面覆蓋表上")

    evidence = {
        C_IDS: f"{len(order)} 個任務從 T001 連號到 {order[-1] if order else 'T000'}",
        C_ANCHOR: "每個 ⚙ 與 📎 的引用都有 § 錨點",
        C_GEAR: f"{sum(len(t['gear']) for t in tasks.values())} 個 ⚙ 錨點都在規格檔裡找得到",
        C_CLIP: "📎 引用的 FR / NFR / SC、R、Q 編號都找得到",
        C_COVER: f"{len(required)} 個必須覆蓋的介面元素都在介面覆蓋表上",
        C_ROW: f"{len(coverage)} 列介面覆蓋的實作與測試任務都存在且 ⚙ 列了該元素",
    }
    checks = [
        {
            "check": check,
            "result": "不過" if violations[check] else "過",
            "evidence": ";".join(f"第 {v['line']} 行:{v['reason']}" if v["line"] else v["text"] + ":" + v["reason"] for v in violations[check][:20])
            if violations[check]
            else evidence[check],
            "violations": violations[check],
        }
        for check in CHECKS
    ]
    passed = not any(violations.values())
    print(f"檢查了 {len(order)} 個任務、{len(coverage)} 列介面覆蓋,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump({"tasks": str(args.tasks), "package": str(args.package), "passed": passed, "checks": checks}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
