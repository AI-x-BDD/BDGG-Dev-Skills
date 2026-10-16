# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查一份 spec.md 的結構是否符合本 skill 的骨架 templates/spec.template.md。

檢查項目:每一行都對得回骨架、沒有殘留填位符號、必填段落齊全且順序正確、每個使用者故事都有驗收情境、功能需求與非功能需求、
FR / NFR / SC 各自全檔連號、全域需求的每一條都標出兩個以上存在的故事、內文引用的編號都存在。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "spec.template.md"
PLACEHOLDER = re.compile(r"\{\{(.+?)\}\}")
STORY_HEADING = re.compile(r"^### 使用者故事 (\d+) - ")
ITEM = re.compile(r"^- \*\*(FR|NFR|SC)-(\d{3})\*\*")
APPLIES = re.compile(r"\(適用:使用者故事 ([^)]*)\)")
REFERENCE = re.compile(r"\b(FR|NFR|SC)-(\d{3})\b")
STORY_PARTS = ["**驗收情境**:", "**功能需求**:", "**非功能需求**:"]

R_LINES = "每一行都對得回骨架"
R_SECTIONS = "必填段落齊全且順序正確"
R_STORY = "每個使用者故事都有驗收情境、功能需求與非功能需求"
R_NUMBER = "FR、NFR、SC 各自全檔連號"
R_GLOBAL = "全域需求標出兩個以上存在的故事"
R_REFERENCE = "引用的編號都存在"
RULES = [R_LINES, R_SECTIONS, R_STORY, R_NUMBER, R_GLOBAL, R_REFERENCE]


def read_lines(path: Path, what: str) -> list[str]:
    if not path.is_file():
        print(f"錯誤: 找不到{what} {path};請給存在的檔案路徑。", file=sys.stderr)
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        print(f"錯誤: {what} {path} 不是 UTF-8 編碼;請轉存成 UTF-8 再執行。", file=sys.stderr)
        sys.exit(2)


def line_pattern(line: str) -> re.Pattern[str]:
    """骨架的一行變成比對樣式:固定的字照原樣,填位符號可以換成任何內容。"""
    parts = PLACEHOLDER.split(line.strip())
    body = "".join(re.escape(part) if index % 2 == 0 else ".*?" for index, part in enumerate(parts))
    return re.compile(f"^{body}$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", required=True, type=Path, help="要檢查的 spec.md 檔案路徑,例如 specs/001-photo-album-organizer/spec.md")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="骨架檔案路徑,預設為本 skill 的 templates/spec.template.md")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    skeleton = [line.strip() for line in read_lines(args.template, "骨架") if line.strip()]
    lines = list(enumerate(read_lines(args.spec, "spec.md"), start=1))
    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}

    def bad(rule: str, number: int, text: str, reason: str) -> None:
        violations[rule].append({"line": number, "text": text, "reason": reason})

    # 每一行都對得回骨架
    patterns = [line_pattern(line) for line in skeleton]
    for number, line in lines:
        text = line.strip()
        if not text:
            continue
        if PLACEHOLDER.search(text):
            bad(R_LINES, number, text, "還留著填位符號 `{{…}}`;換成具體內容")
        elif not any(pattern.match(text) for pattern in patterns):
            bad(R_LINES, number, text, "對不回骨架的任何一行:骨架沒有這一行,或骨架裡固定的字被改了")

    # 必填段落齊全且順序正確
    expected = [line for line in skeleton if line.startswith("## ")]
    found = [(number, line.strip()) for number, line in lines if line.startswith("## ")]
    found_titles = [title for _, title in found]
    for title in expected:
        if title not in found_titles:
            bad(R_SECTIONS, 0, title, "缺少這個段落")
    order = [title for title in found_titles if title in expected]
    if order != [title for title in expected if title in order]:
        bad(R_SECTIONS, 0, " → ".join(order), "段落順序和骨架不同:" + " → ".join(expected))

    # 切出每個使用者故事與全域需求的範圍
    stories: dict[int, list[tuple[int, str]]] = {}
    global_lines: list[tuple[int, str]] = []
    current: list[tuple[int, str]] | None = None
    for number, line in lines:
        heading = STORY_HEADING.match(line)
        if heading:
            current = stories.setdefault(int(heading.group(1)), [])
            current.append((number, line))
            continue
        if line.startswith("## 全域需求"):
            current = global_lines
            continue
        if line.startswith("## ") or line.startswith("### 邊界情況"):
            current = None
            continue
        if current is not None:
            current.append((number, line))

    if not stories:
        bad(R_STORY, 0, "", "找不到任何 `### 使用者故事 <序號> - ` 標題")
    if sorted(stories) != list(range(1, len(stories) + 1)):
        bad(R_STORY, 0, "、".join(map(str, sorted(stories))), "使用者故事的序號要從 1 開始連號")
    for story, block in stories.items():
        texts = [text.strip() for _, text in block]
        for part in STORY_PARTS:
            if part not in texts:
                bad(R_STORY, block[0][0], block[0][1].strip(), f"使用者故事 {story} 缺少 `{part}`")
        if not any(ITEM.match(text) for text in texts if text.startswith("- **FR-")):
            bad(R_STORY, block[0][0], block[0][1].strip(), f"使用者故事 {story} 的功能需求底下沒有任何一條 FR")

    # FR、NFR、SC 各自全檔連號
    defined: dict[str, list[int]] = {"FR": [], "NFR": [], "SC": []}
    for number, line in lines:
        item = ITEM.match(line.strip())
        if item:
            kind, value = item.group(1), int(item.group(2))
            expected_value = len(defined[kind]) + 1
            if value != expected_value:
                bad(R_NUMBER, number, line.strip(), f"預期是 {kind}-{expected_value:03d};編號要依出現順序全檔連號、不重複")
            defined[kind].append(value)

    # 全域需求標出兩個以上存在的故事
    for number, line in global_lines:
        text = line.strip()
        if not ITEM.match(text):
            continue
        applies = APPLIES.search(text)
        if not applies:
            bad(R_GLOBAL, number, text, "全域需求要寫出 `(適用:使用者故事 <序號>、<序號>)`")
            continue
        listed = [part.strip() for part in applies.group(1).split("、")]
        if not all(part.isdigit() for part in listed):
            bad(R_GLOBAL, number, text, "適用的故事要寫成以「、」分隔的序號,例如 `1、3`")
            continue
        numbers = [int(part) for part in listed]
        if len(set(numbers)) < 2:
            bad(R_GLOBAL, number, text, "只適用一個故事的需求要放在那個故事底下,不放進全域需求")
        missing = [n for n in numbers if n not in stories]
        if missing:
            bad(R_GLOBAL, number, text, f"適用的使用者故事 {'、'.join(map(str, missing))} 不存在")

    # 引用的編號都存在
    for number, line in lines:
        text = line.strip()
        item = ITEM.match(text)
        body = text[item.end():] if item else text
        for kind, value in REFERENCE.findall(body):
            if int(value) not in defined[kind]:
                bad(R_REFERENCE, number, text, f"引用的 {kind}-{value} 沒有在這份規格裡定義")

    checks = [
        {"rule": rule, "result": "不過" if violations[rule] else "過", "violations": violations[rule]}
        for rule in RULES
    ]
    passed = not any(violations.values())
    report = {
        "spec": args.spec.as_posix(),
        "passed": passed,
        "counts": {"stories": len(stories), **{kind: len(values) for kind, values in defined.items()}},
        "checks": checks,
    }
    print(f"檢查了 {len(lines)} 行,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
