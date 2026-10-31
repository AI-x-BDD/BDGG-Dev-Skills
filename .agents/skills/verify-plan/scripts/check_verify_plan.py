# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查 verify-plan.md 是否涵蓋 spec.md 的每條 SC 與每個使用者故事,且每一列都填完。

結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

COLUMNS = ["V", "對象", "真實元件", "自動測試的替身", "實跑做法", "樣本", "通過條件", "副作用與護欄", "判定者"]
SC = re.compile(r"SC-\d{3}")
STORY_HEADING = re.compile(r"^### 使用者故事 (\d+) - ", re.MULTILINE)
SC_LINE = re.compile(r"^- \*\*(SC-\d{3})\*\*", re.MULTILINE)
STORY_REF = re.compile(r"故事 (\d+)")
R_COLUMNS = "表頭照骨架且每一格都有內容"
R_COVER = "每條 SC 與每個使用者故事都有驗收項"
R_NUMBER = "V 編號從 1 連號"


def read(path: Path, what: str) -> str:
    if not path.is_file():
        print(f"錯誤: 找不到 {what} {path};請給存在的檔案路徑。", file=sys.stderr)
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"錯誤: {what} {path} 不是 UTF-8 編碼;請轉存成 UTF-8 再執行。", file=sys.stderr)
        sys.exit(2)


def cells(line: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verify-plan", required=True, type=Path, help="要檢查的 verify-plan.md 路徑,例如 specs/005-x/verify-plan.md")
    parser.add_argument("--spec", required=True, type=Path, help="對照用的 spec.md 路徑,例如 specs/005-x/spec.md")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    text, spec = read(args.verify_plan, "verify-plan.md"), read(args.spec, "spec.md")
    violations: dict[str, list[str]] = {R_COLUMNS: [], R_COVER: [], R_NUMBER: []}
    rows: list[list[str]] = []
    header = None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|") or re.match(r"^\|[\s:|-]+\|$", line):
            continue
        row = cells(line)
        if header is None:
            header = row
            if row != COLUMNS:
                violations[R_COLUMNS].append(f"第 {number} 行的表頭不是 {COLUMNS}")
            continue
        if len(row) != len(COLUMNS) or not all(row):
            violations[R_COLUMNS].append(f"第 {number} 行有空格或欄數不對")
        rows.append(row)
    for index, row in enumerate(rows, 1):
        if row[0] != f"V{index}":
            violations[R_NUMBER].append(f"第 {index} 列的編號是 {row[0]},預期 V{index}")
    targets = " ".join(row[1] for row in rows if len(row) > 1)
    covered_sc, covered_story = set(SC.findall(targets)), set(STORY_REF.findall(targets))
    for sc in SC_LINE.findall(spec):
        if sc not in covered_sc:
            violations[R_COVER].append(f"{sc} 沒有驗收項")
    for story in STORY_HEADING.findall(spec):
        if story not in covered_story:
            violations[R_COVER].append(f"使用者故事 {story} 沒有驗收項")

    passed = not any(violations.values())
    print(f"檢查了 {len(rows)} 個驗收項,{sum(map(len, violations.values()))} 個不符項", file=sys.stderr)
    print(json.dumps({"passed": passed, "checks": [{"rule": k, "result": "不過" if v else "過", "violations": v} for k, v in violations.items()]}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
