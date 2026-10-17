# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查一份 techstack.md 的結構是否符合本 skill 的骨架 templates/techstack.template.md,並對照同資料夾的 research.md。

檢查項目:五節齊全且順序正確、一覽表每一列的層只用七類且一列一個技術、依賴四類齊全且個數和列出的一致、
每一項都指回 research.md 裡存在的研究項。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = ["一覽", "依賴", "新引入與沿用", "自寫取代套件", "刻意不用"]
LAYERS = ["前端", "後端", "資料", "領域", "測試", "交付", "部署"]
DEPENDENCY_KINDS = ["後端 runtime", "前端 runtime", "開發", "系統套件"]
RESEARCH_HEADING = re.compile(r"^## R(\d+)\.")
R_REFERENCE = re.compile(r"R(\d+)")
DECISION_CELL = re.compile(r"^R\d+(、R\d+)*$")
TRAILING_REFERENCE = re.compile(r"[((]R\d+(、R\d+)*[))]$")
DEPENDENCY_LINE = re.compile(r"^- (後端 runtime|前端 runtime|開發|系統套件)[((](?:[^,,))]+[,,])?(\d+) 個[))][::](.*)$")
SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")

R_SECTIONS = "五節齊全且順序正確"
R_TABLE = "一覽表的層只用七類且一列一個技術"
R_DEPENDENCY = "依賴四類齊全且個數和列出的一致"
R_REFERENCE_EXISTS = "每一項都指回存在的研究項"
RULES = [R_SECTIONS, R_TABLE, R_DEPENDENCY, R_REFERENCE_EXISTS]


def read_lines(path: Path, what: str) -> list[str]:
    if not path.is_file():
        print(f"錯誤: 找不到 {what} {path};請給存在的檔案路徑。", file=sys.stderr)
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        print(f"錯誤: {what} {path} 不是 UTF-8 編碼;請轉存成 UTF-8 再執行。", file=sys.stderr)
        sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--techstack", required=True, type=Path, help="要檢查的 techstack.md 檔案路徑,例如 specs/001-photo-album-organizer/techstack.md")
    parser.add_argument("--research", type=Path, help="對照用的 research.md 路徑,預設為 techstack.md 同資料夾的 research.md")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    lines = read_lines(args.techstack, "techstack.md")
    research_path = args.research or args.techstack.parent / "research.md"
    defined = {int(m.group(1)) for line in read_lines(research_path, "research.md") if (m := RESEARCH_HEADING.match(line))}
    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}

    def bad(rule: str, number: int, text: str, reason: str) -> None:
        violations[rule].append({"line": number, "text": text, "reason": reason})

    def check_references(number: int, text: str, refs: str) -> None:
        for value in R_REFERENCE.findall(refs):
            if int(value) not in defined:
                bad(R_REFERENCE_EXISTS, number, text, f"R{value} 不在 {research_path.as_posix()} 裡;research.md 有的是 R1–R{max(defined, default=0)}")

    # 依 `## ` 標題切成各節
    sections: dict[str, list[tuple[int, str]]] = {}
    order: list[str] = []
    current = None
    for number, line in enumerate(lines, start=1):
        if line.startswith("## "):
            current = line[3:].strip()
            order.append(current)
            sections[current] = []
        elif current is not None:
            sections[current].append((number, line.strip()))
    if order != SECTIONS:
        bad(R_SECTIONS, 0, "", f"`##` 標題要依序是 {'、'.join(SECTIONS)};實際是 {'、'.join(order) or '都沒有'}")

    rows = [(n, text) for n, text in sections.get("一覽", []) if text.startswith("|") and not SEPARATOR.match(text)]
    if not rows[1:]:
        bad(R_TABLE, 0, "", "一覽表沒有任何一列技術")
    for n, text in rows[1:]:  # 第一列是表頭
        cells = [cell.strip() for cell in text.strip("|").split("|")]
        if len(cells) != 5:
            bad(R_TABLE, n, text, f"一覽表每一列要有 5 欄(層、技術、版本、用途、決策),這一列有 {len(cells)} 欄")
            continue
        layer, technology, version, _, decision = cells
        if layer not in LAYERS:
            bad(R_TABLE, n, text, f"層只能是 {'、'.join(LAYERS)} 其中之一,實際是 `{layer}`")
        if "、" in technology:
            bad(R_TABLE, n, text, "一列只放一個技術;把「、」分開的技術各拆成一列")
        if not version:
            bad(R_TABLE, n, text, "版本欄不能空;沒定寫「未定」,沒有版本可言寫「不適用」")
        if not DECISION_CELL.match(decision):
            bad(R_REFERENCE_EXISTS, n, text, "決策欄要寫成 `R<序號>`,多個以「、」分隔")
        check_references(n, text, decision)

    found_kinds = []
    for n, text in sections.get("依賴", []):
        if not text.startswith("- "):
            continue
        match = DEPENDENCY_LINE.match(text)
        if not match:
            bad(R_DEPENDENCY, n, text, f"依賴每一行要寫成 `- <類別>(<個數> 個):…`,類別是 {'、'.join(DEPENDENCY_KINDS)}")
            continue
        kind, count, body = match.group(1), int(match.group(2)), match.group(3).strip()
        found_kinds.append(kind)
        listed = re.findall(r"`[^`]+`[((]R\d+[))]", body)
        if count == 0 and not re.fullmatch(r"無[((]R\d+[))]", body):
            bad(R_DEPENDENCY, n, text, "個數是 0 時寫成 `無(R<序號>)`")
        elif count and len(listed) != count:
            bad(R_DEPENDENCY, n, text, f"標的個數是 {count},實際列出 {len(listed)} 個 `套件名`(R序號)")
        check_references(n, text, body)
    if found_kinds != DEPENDENCY_KINDS:
        bad(R_DEPENDENCY, 0, "", f"依賴要依序列出 {'、'.join(DEPENDENCY_KINDS)} 四類;實際是 {'、'.join(found_kinds) or '都沒有'}")

    for name in SECTIONS[2:]:
        for n, text in sections.get(name, []):
            if not text.startswith("- "):
                continue
            if name == "新引入與沿用":
                # 沿用那一行每個服務各自帶 (R序號),只要求整行至少有一個並且都存在
                if not re.search(r"[((]R\d+[))]", text):
                    bad(R_REFERENCE_EXISTS, n, text, "每一項都要以 (R序號) 指回 research.md")
            elif not TRAILING_REFERENCE.search(text):
                bad(R_REFERENCE_EXISTS, n, text, "這一項要以 (R序號) 結尾,指回 research.md")
            check_references(n, text, " ".join(re.findall(r"[((]([^))]*)[))]", text)))

    checks = [{"rule": rule, "result": "不過" if violations[rule] else "過", "violations": violations[rule]} for rule in RULES]
    passed = not any(violations.values())
    report = {
        "techstack": args.techstack.as_posix(),
        "research": research_path.as_posix(),
        "passed": passed,
        "counts": {"technologies": len(rows[1:]), "research_items": len(defined)},
        "checks": checks,
    }
    print(f"檢查了 {len(rows[1:])} 個技術,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
