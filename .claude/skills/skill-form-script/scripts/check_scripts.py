# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查目標 skill 的 scripts/ 底下每一支腳本的結構,以及 rules/腳本執行-規範.md 是否照固定內容寫。

判 腳本-格式規範.md 與 腳本執行規範-格式規範.md 裡結果只由檔案內容決定的 8 條 Rule(其中 2 條只判一部分),
結果以 JSON 寫到 stdout;有任何一條不過時 exit code 是 1。
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

R_PY = "腳本只用 Python 寫"
R_SINGLE = "腳本單檔自足"
R_PEP = "第三方套件宣告在檔頭的 PEP 723 區塊"
R_RANGE = "每個第三方套件寫版本範圍"
R_ARGS = "輸入只走命令列參數"
R_HELP = "`--help` 說明用途與每個參數"
R_ENC = "讀寫文字檔明確指定 encoding"
R_FIXED = "腳本執行規範照固定內容寫"

SCRIPT_RULES = "腳本-格式規範.md"
FIXED_RULES = "腳本執行規範-格式規範.md"
# (Rule 名稱, 所在的規範檔, 只判一部分時留給執行的人對照的那一半);8 條的強度都是 must
RULES = [
    (R_PY, SCRIPT_RULES, None),
    (R_SINGLE, SCRIPT_RULES, None),
    (R_PEP, SCRIPT_RULES, None),
    (R_RANGE, SCRIPT_RULES, None),
    (R_ARGS, SCRIPT_RULES, "腳本只判有沒有用 argparse、有沒有呼叫 input();會不會用別的方式停下來等確認,請自己對照"),
    (R_HELP, SCRIPT_RULES, "腳本只判 description 與每個參數的 help 有沒有寫;寫得夠不夠讓人知道參數怎麼下,請自己對照"),
    (R_ENC, SCRIPT_RULES, None),
    (R_FIXED, FIXED_RULES, None),
]

PEP723 = re.compile(r"\A# /// script\n((?:#.*\n)*?)# ///\n")
FIXED_CONTENT = re.compile(r"^````markdown\n(.*?)\n````[ \t]*$", re.MULTILINE | re.DOTALL)
EXTRA_DEPENDENCY_FILES = ("requirements.txt", "pyproject.toml", "uv.lock", ".venv")


def fail(message: str) -> None:
    print(f"錯誤: {message}", file=sys.stderr)
    sys.exit(2)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        fail(f"{path} 不是 UTF-8 編碼。請把它轉存成 UTF-8 再執行。")
    return ""


def fixed_content() -> str:
    """從本 skill 的 rules/腳本執行規範-格式規範.md 讀出腳本執行規範的固定內容。"""
    source = Path(__file__).resolve().parent.parent / "rules" / FIXED_RULES
    if not source.is_file():
        fail(f"找不到 {source}。這支腳本要和它所在 skill 的 `rules/{FIXED_RULES}` 放在一起才比對得了固定內容。")
    match = FIXED_CONTENT.search(read_text(source))
    if not match:
        fail(f"{source} 裡找不到用 ````markdown 包起來的固定內容。")
    return match.group(1)


def call_name(node: ast.Call) -> tuple[str, bool]:
    """回傳 (被呼叫的名字, 是不是直接以名字呼叫)。"""
    if isinstance(node.func, ast.Name):
        return node.func.id, True
    if isinstance(node.func, ast.Attribute):
        return node.func.attr, False
    return "", False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", required=True, type=Path, help="目標 skill 的根目錄(含 SKILL.md 的那一層)")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not (args.skill / "SKILL.md").is_file():
        fail(f"{args.skill} 底下沒有 SKILL.md。--skill 要給 skill 的根目錄(含 SKILL.md 的那一層)。")

    violations: dict[str, list[dict]] = {rule: [] for rule, _, _ in RULES}

    def bad(rule: str, path: Path, reason: str, line: int = 0, text: str = "") -> None:
        violations[rule].append({"file": path.relative_to(args.skill).as_posix(), "line": line, "text": text.strip(), "reason": reason})

    scripts_dir = args.skill / "scripts"
    files = (
        sorted(p for p in scripts_dir.rglob("*") if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith("."))
        if scripts_dir.is_dir()
        else []
    )
    scripts = [p for p in files if p.suffix == ".py"]
    for path in files:
        if path.suffix != ".py":
            bad(R_PY, path, "`scripts/` 底下只放 `.py`;這個檔要改寫成 Python 腳本")
    if files:
        for base in (scripts_dir, args.skill):
            for name in EXTRA_DEPENDENCY_FILES:
                if (base / name).exists():
                    bad(R_PEP, base / name, "依賴只寫在腳本檔頭的 PEP 723 區塊,不另外放這個檔")

    stems = {p.stem for p in scripts}
    dependency_count = 0
    argument_count = 0
    text_io_count = 0
    for path in scripts:
        source = read_text(path)
        lines = source.splitlines()

        def line_text(number: int) -> str:
            return lines[number - 1] if 0 < number <= len(lines) else ""

        try:
            tree = ast.parse(source)
        except SyntaxError as error:
            fail(f"{path} 第 {error.lineno} 行有語法錯誤({error.msg}),解析不了。先讓它能以 `uv run` 執行再檢查。")

        header = PEP723.match(source)
        if not header:
            bad(R_PEP, path, "檔案最前面沒有 PEP 723 區塊;第一行要是 `# /// script`,列出 `requires-python` 與 `dependencies`", 1, line_text(1))
        else:
            block = "\n".join(line[1:].strip() for line in header.group(1).splitlines())
            if not re.search(r"^requires-python\s*=", block, re.MULTILINE):
                bad(R_PEP, path, "PEP 723 區塊裡沒有 `requires-python`", 1, line_text(1))
            dependencies = re.search(r"^dependencies\s*=\s*\[(.*?)\]", block, re.MULTILINE | re.DOTALL)
            if not dependencies:
                bad(R_PEP, path, "PEP 723 區塊裡沒有 `dependencies`;只用標準函式庫也要寫 `dependencies = []`", 1, line_text(1))
            else:
                for dependency in re.findall(r"""["']([^"']+)["']""", dependencies.group(1)):
                    dependency_count += 1
                    has_lower = re.search(r">=\s*[\w.]+", dependency)
                    has_upper = re.search(r"<\s*[\w.]+", dependency.replace(">=", ""))
                    if not (has_lower and has_upper):
                        number = next((n for n, line in enumerate(lines, start=1) if dependency in line), 1)
                        bad(R_RANGE, path, f"`{dependency}` 要寫出下限與上限,例如 `<套件名>>=<下限>,<<下一個主版本>`", number, line_text(number))

        uses_argparse = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    uses_argparse = uses_argparse or top == "argparse"
                    if top in stems - {path.stem}:
                        bad(R_SINGLE, path, f"import 了同目錄的 `{top}.py`;用得到的程式碼要寫在這一個檔裡", node.lineno, line_text(node.lineno))
            elif isinstance(node, ast.ImportFrom):
                top = (node.module or "").split(".")[0]
                uses_argparse = uses_argparse or top == "argparse"
                if node.level or top in stems - {path.stem}:
                    bad(R_SINGLE, path, "import 了 skill 裡的其他 `.py`;用得到的程式碼要寫在這一個檔裡", node.lineno, line_text(node.lineno))
            elif isinstance(node, ast.Call):
                name, direct = call_name(node)
                keywords = {keyword.arg for keyword in node.keywords}
                if name == "input" and direct:
                    bad(R_ARGS, path, "呼叫了 `input()`;輸入改成 `argparse` 的命令列參數", node.lineno, line_text(node.lineno))
                elif name == "ArgumentParser":
                    described = next((k.value for k in node.keywords if k.arg == "description"), None)
                    from_docstring = isinstance(described, ast.Name) and described.id == "__doc__"
                    if described is None or (from_docstring and not ast.get_docstring(tree)):
                        bad(R_HELP, path, "`ArgumentParser` 沒有 description;寫出這支腳本做什麼", node.lineno, line_text(node.lineno))
                elif name == "add_argument" and not direct:
                    argument_count += 1
                    if "help" not in keywords:
                        bad(R_HELP, path, "這個參數沒有 `help`;寫出要給它什麼", node.lineno, line_text(node.lineno))
                elif name in ("read_text", "write_text") and not direct:
                    text_io_count += 1
                    if "encoding" not in keywords:
                        bad(R_ENC, path, f"`{name}()` 沒有寫 `encoding`;沒有理由用別的就寫 `encoding=\"utf-8\"`", node.lineno, line_text(node.lineno))
                elif name == "open" and direct:
                    mode = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "mode"), None)
                    if isinstance(mode, ast.Constant) and "b" in str(mode.value):
                        continue
                    text_io_count += 1
                    if "encoding" not in keywords:
                        bad(R_ENC, path, "`open()` 沒有寫 `encoding`;沒有理由用別的就寫 `encoding=\"utf-8\"`", node.lineno, line_text(node.lineno))
        if not uses_argparse:
            bad(R_ARGS, path, "沒有用 `argparse`;每一項輸入都定義成命令列參數,`--help` 才印得出用法")

    if scripts:
        target = args.skill / "rules" / "腳本執行-規範.md"
        if not target.is_file():
            bad(R_FIXED, target, "這支 skill 有腳本,卻沒有 `rules/腳本執行-規範.md`;照固定內容補上")
        else:
            expected = fixed_content().strip().splitlines()
            actual = read_text(target).strip().splitlines()
            if actual != expected:
                number = next((n for n, (a, e) in enumerate(zip(actual, expected), start=1) if a != e), min(len(actual), len(expected)) + 1)
                shown = actual[number - 1] if number <= len(actual) else ""
                bad(R_FIXED, target, f"從第 {number} 行起和固定內容不同(這個檔 {len(actual)} 行,固定內容 {len(expected)} 行);照固定內容照抄,不改寫", number, shown)

    count = len(scripts)
    none = "`scripts/` 底下沒有腳本"
    passed_evidence = {
        R_PY: f"`scripts/` 底下 {len(files)} 個檔都是 `.py`" if files else none,
        R_SINGLE: f"{count} 支腳本都沒有 import skill 裡的其他 `.py`" if count else none,
        R_PEP: f"{count} 支腳本的檔頭都有 PEP 723 區塊,沒有另外放依賴檔" if count else none,
        R_RANGE: (f"{dependency_count} 個第三方套件都寫了下限與上限" if dependency_count else "沒有第三方套件") if count else none,
        R_ARGS: f"{count} 支腳本都用 `argparse`,沒有呼叫 `input()`" if count else none,
        R_HELP: f"{count} 支腳本的 `ArgumentParser` 都有 description,{argument_count} 個參數都有 help" if count else none,
        R_ENC: (f"{text_io_count} 處讀寫文字檔都寫了 `encoding`" if text_io_count else "沒有讀寫文字檔") if count else none,
        R_FIXED: "`rules/腳本執行-規範.md` 與固定內容一字不差" if count else none,
    }
    checks = []
    for rule, source, partial in RULES:
        mine = violations[rule]
        checks.append(
            {
                "rule": rule,
                "source": source,
                "strength": "must",
                "result": "不過" if mine else "過",
                "evidence": ";".join(v["file"] + (f" 第 {v['line']} 行" if v["line"] else "") + f":{v['reason']}" for v in mine) if mine else passed_evidence[rule],
                "partial": partial,
                "violations": mine,
            }
        )
    passed = not any(violations.values())
    report = {
        "skill": str(args.skill),
        "passed": passed,
        "scripts": [p.relative_to(args.skill).as_posix() for p in scripts],
        "checks": checks,
    }
    print(f"檢查了 {count} 支腳本,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
