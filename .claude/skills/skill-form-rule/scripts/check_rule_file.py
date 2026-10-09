# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查 Rule File 的結構:標題格式、流水號、四段的順序、example 成對與說明行、有沒有用流水號引用 Rule。"""
import argparse
import json
import re
import sys
from pathlib import Path

RULE_TITLE = re.compile(r"^# Rule (\d+) \[(must|should)\] - \S.*$")
FENCE = re.compile(r"^(`{3,})(.*)$")
WHY = re.compile(r"^- 為什麼:")
NUMBER_REFERENCE = re.compile(r"〈Rule \d+〉")
GOOD = "## good example"
BAD = "## bad example"
FENCE_OPEN = None


def outside_fences(lines: list[str]) -> tuple[list[tuple[int, str | None]], int]:
    """回傳 code fence 以外的 (行號, 內容);fence 開始的那一行以內容 None 標出。

    第二個回傳值是沒有關閉的 fence 開始的行號,都有關閉時是 0。
    """
    visible: list[tuple[int, str | None]] = []
    open_length = 0
    open_line = 0
    for number, line in enumerate(lines, start=1):
        match = FENCE.match(line)
        if match:
            length = len(match.group(1))
            if open_length == 0:
                open_length, open_line = length, number
                visible.append((number, FENCE_OPEN))
            elif length >= open_length and match.group(2).strip() == "":
                open_length = 0
            continue
        if open_length == 0:
            visible.append((number, line))
    return visible, (open_line if open_length else 0)


def check(lines: list[str]) -> tuple[int, list[dict]]:
    """回傳 (Rule 的條數, 不符項的清單)。"""
    problems: list[dict] = []

    def report(line: int, rule: str, message: str) -> None:
        problems.append({"line": line, "rule": rule, "message": message})

    visible, unclosed = outside_fences(lines)
    if unclosed:
        report(unclosed, "每條 Rule 照固定格式寫", "這一行開始的 code fence 沒有關閉")

    rules: list[dict] = []
    current: dict | None = None
    waiting = 0  # 還在等說明行的 example section 的行號
    content_before_first_rule = False

    def missing_explanation() -> None:
        nonlocal waiting
        if waiting:
            report(waiting, "每條 Rule 照固定格式寫", "這個 example 沒有先用一行 `- ` 說明重點")
            waiting = 0

    for number, line in visible:
        if line is FENCE_OPEN:
            if waiting:
                report(waiting, "每條 Rule 照固定格式寫", "這個 example 的說明要寫在案例資料之前")
                waiting = 0
            continue
        if line.startswith("# "):
            missing_explanation()
            match = RULE_TITLE.match(line.rstrip())
            if match:
                current = {"number": int(match.group(1)), "line": number, "sections": [], "bullets": 0, "why": 0}
                rules.append(current)
            else:
                current = None
                report(
                    number,
                    "Rule File 只由 Rule 組成",
                    "`#` 標題要寫成 `# Rule <流水號> [must 或 should] - <Rule 名稱>`",
                )
            continue
        if line.startswith("#"):
            missing_explanation()
            if current is None:
                continue
            title = line.rstrip()
            if title in (GOOD, BAD):
                current["sections"].append((title, number))
                waiting = number
            else:
                report(number, "每條 Rule 照固定格式寫", "Rule 底下只能有 `## good example` 與 `## bad example` 兩種 section")
            continue
        if not line.strip():
            continue
        if current is None:
            if not rules and not content_before_first_rule:
                content_before_first_rule = True
                report(number, "Rule File 只由 Rule 組成", "第一條 Rule 之前有其他內容")
            continue
        if not current["sections"]:
            if line.startswith("- "):
                current["bullets"] += 1
                if WHY.match(line):
                    current["why"] += 1
            if NUMBER_REFERENCE.search(line):
                report(number, "用名稱引用 Rule", "desc 用流水號引用了 Rule,要寫成〈Rule 名稱〉")
        elif waiting:
            if not line.startswith("- "):
                report(waiting, "每條 Rule 照固定格式寫", "這個 example 的第一行要先用一行 `- ` 說明重點")
            waiting = 0
    missing_explanation()

    if not rules:
        report(1, "Rule File 只由 Rule 組成", "檔案裡沒有任何一條 Rule")

    for index, rule in enumerate(rules, start=1):
        if rule["number"] != index:
            report(rule["line"], "每條 Rule 照固定格式寫", f"流水號要從 1 連續編下去:這一條應該是 {index},寫的是 {rule['number']}")
        if rule["bullets"] == 0:
            report(rule["line"], "每條 Rule 照固定格式寫", "這條 Rule 沒有 desc")
        if rule["why"] == 0:
            report(rule["line"], "desc 寫出為什麼", "desc 沒有 `- 為什麼:` 這一行")
        sections = rule["sections"]
        if not sections:
            report(rule["line"], "每條 Rule 照固定格式寫", "這條 Rule 沒有 `## good example` 與 `## bad example`")
            continue
        for position, (title, line) in enumerate(sections):
            expected = GOOD if position % 2 == 0 else BAD
            if title != expected:
                report(line, "每條 Rule 照固定格式寫", f"example 要一組一組寫,good 在前、bad 緊接在後:這裡應該是 `{expected}`")
                break
        else:
            if len(sections) % 2 == 1:
                report(sections[-1][1], "每條 Rule 照固定格式寫", "最後一組只有 good example,缺 `## bad example`")

    problems.sort(key=lambda problem: problem["line"])
    return len(rules), problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path, help="要檢查的 Rule File 的路徑(目標 skill 的 rules/ 底下的 .md 檔)")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not args.file.is_file():
        print(f"錯誤: {args.file} 不是檔案。--file 要給 Rule File 的路徑(目標 skill 的 rules/ 底下的 .md 檔)。", file=sys.stderr)
        return 1
    try:
        text = args.file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"錯誤: {args.file} 不是 UTF-8 編碼的文字檔。Rule File 要存成 UTF-8。", file=sys.stderr)
        return 1

    count, problems = check(text.splitlines())
    print(f"檢查了 {count} 條 Rule,{len(problems)} 個不符項", file=sys.stderr)
    json.dump({"file": args.file.as_posix(), "rules": count, "problems": problems}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
