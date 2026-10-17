# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查一份 research.md 的結構是否符合本 skill 的骨架 templates/research.template.md。

檢查項目:研究項標題標出對應且從 R1 連號、每個研究項依序有決策、理由、考慮過的替代方案三段、
理由的每一條都以四類證據之一開頭、待驗證與修訂紀錄兩節都在且引用的研究項都存在。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 半形與全形的括號、冒號都接受
OPEN, CLOSE, COLON = "[((]", "[))]", "[::]"
R_HEADING = re.compile(r"^## R(\d+)\.")
R_HEADING_FULL = re.compile(rf"^## R(\d+)\. (.+?){OPEN}(.*){CLOSE}$")
PARTS = ["決策", "理由", "考慮過的替代方案"]
PART_LABEL = re.compile(rf"^\*\*({'|'.join(PARTS)})\*\*{COLON}")
EVIDENCE = re.compile(rf"^- (?:(實測|估算|查證){OPEN}([^))]*){CLOSE}|判斷{COLON})")
TABLE_ROW = re.compile(r"^\|(.+)\|$")
SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")
REVISION_ITEM = re.compile(rf"^- R(\d+){COLON}")
SECTIONS = ["待驗證", "修訂紀錄"]

R_TITLE = "研究項標題標出對應且從 R1 連號"
R_PARTS = "每個研究項依序有決策、理由、考慮過的替代方案三段"
R_EVIDENCE = "理由的每一條都以四類證據之一開頭"
R_TAIL = "待驗證與修訂紀錄兩節都在且引用的研究項都存在"
RULES = [R_TITLE, R_PARTS, R_EVIDENCE, R_TAIL]


def read_lines(path: Path) -> list[str]:
    if not path.is_file():
        print(f"錯誤: 找不到 research.md {path};請給存在的檔案路徑。", file=sys.stderr)
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        print(f"錯誤: {path} 不是 UTF-8 編碼;請轉存成 UTF-8 再執行。", file=sys.stderr)
        sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--research", required=True, type=Path, help="要檢查的 research.md 檔案路徑,例如 specs/001-photo-album-organizer/research.md")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    lines = read_lines(args.research)
    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}

    def bad(rule: str, number: int, text: str, reason: str) -> None:
        violations[rule].append({"line": number, "text": text, "reason": reason})

    # 依 `## ` 標題切出研究項與文末兩節,每段記下起訖行
    blocks: list[tuple[int, str, list[tuple[int, str]]]] = []
    for number, line in enumerate(lines, start=1):
        if line.startswith("## "):
            blocks.append((number, line.strip(), []))
        elif blocks:
            blocks[-1][2].append((number, line))

    research = [block for block in blocks if R_HEADING.match(block[1])]
    numbers: list[int] = []
    for number, heading, _ in research:
        full = R_HEADING_FULL.match(heading)
        if not full:
            bad(R_TITLE, number, heading, "標題要寫成 `## R<序號>. <主題>(<對應的 FR、NFR、SC、憲法原則或使用者指定>)`")
        elif not full.group(3).strip():
            bad(R_TITLE, number, heading, "括號裡的對應是空的;寫出這個研究項對應的 FR、NFR、SC、憲法原則或「使用者指定」")
        numbers.append(int(R_HEADING.match(heading).group(1)))
    if not research:
        bad(R_TITLE, 0, "", "找不到任何 `## R<序號>.` 研究項;每個研究項各寫一個二級標題")
    for expected, (actual, (number, heading, _)) in enumerate(zip(numbers, research), start=1):
        if actual != expected:
            bad(R_TITLE, number, heading, f"研究項要從 R1 連號,這裡應該是 R{expected}")
            break

    for number, heading, body in research:
        found = [(n, PART_LABEL.match(line.strip()).group(1)) for n, line in body if PART_LABEL.match(line.strip())]
        names = [name for _, name in found]
        if names != PARTS:
            bad(R_PARTS, number, heading, f"三段要依序各出現一次:{'、'.join(PARTS)};實際是 {'、'.join(names) or '都沒有'}")
        if "理由" not in names:
            continue
        # 理由段從「理由」標籤到下一個標籤;後面沒有標籤就到這個研究項結束
        index = names.index("理由")
        start = found[index][0]
        end = found[index + 1][0] if index + 1 < len(found) else body[-1][0] + 1
        for n, line in body:
            # 只看理由段的頂層條列;縮排的子項與表格屬於上一條
            if start < n < end and line.startswith("- "):
                match = EVIDENCE.match(line)
                if not match:
                    bad(R_EVIDENCE, n, line.strip(), "理由的每一條要以 `實測(<量測環境>)`、`估算(<依據>)`、`查證(<來源>)` 或 `判斷:` 開頭")
                elif match.group(1) and not match.group(2).strip():
                    bad(R_EVIDENCE, n, line.strip(), f"`{match.group(1)}` 後面的括號是空的;寫出{ {'實測': '量測環境', '估算': '依據', '查證': '來源'}[match.group(1)] }")

    defined = set(numbers)
    tails = {heading[3:].strip(): (number, body) for number, heading, body in blocks if heading[3:].strip() in SECTIONS}
    for name in SECTIONS:
        if name not in tails:
            bad(R_TAIL, 0, "", f"缺少 `## {name}` 這一節")
    if "待驗證" in tails:
        rows = [(n, line.strip()) for n, line in tails["待驗證"][1] if TABLE_ROW.match(line.strip()) and not SEPARATOR.match(line.strip())]
        for n, text in rows[1:]:  # 第一列是表頭
            cells = [cell.strip() for cell in text.strip("|").split("|")]
            source = re.fullmatch(r"R(\d+)", cells[0])
            if not source or int(source.group(1)) not in defined:
                bad(R_TAIL, n, text, f"「來源」欄要是這份文件裡存在的研究項(R1–R{max(defined, default=0)}),實際是 `{cells[0]}`")
            if len(cells) < 4 or cells[3] not in ("是", "否"):
                bad(R_TAIL, n, text, "「擋計畫?」欄只能填「是」或「否」")
    if "修訂紀錄" in tails:
        for n, line in tails["修訂紀錄"][1]:
            if line.startswith("- "):
                item = REVISION_ITEM.match(line)
                if not item or int(item.group(1)) not in defined:
                    bad(R_TAIL, n, line.strip(), "修訂紀錄每一條要以存在的研究項開頭,寫成 `- R<序號>:…`")

    checks = [{"rule": rule, "result": "不過" if violations[rule] else "過", "violations": violations[rule]} for rule in RULES]
    passed = not any(violations.values())
    report = {
        "research": args.research.as_posix(),
        "passed": passed,
        "counts": {"research_items": len(research)},
        "checks": checks,
    }
    print(f"檢查了 {len(research)} 個研究項,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
