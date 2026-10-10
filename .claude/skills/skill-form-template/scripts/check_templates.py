# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查目標 skill 的 templates/ 底下每一份樣板的結構:骨架與範例是否成對、路徑命名是否固定、範例是否就是骨架填完填位符號的樣子。

判 樣板-格式規範.md 裡結果只由檔案內容決定的 3 條 Rule,結果以 JSON 寫到 stdout;有任何一條不過時 exit code 是 1。
填位符號只認 `{{名稱}}` 這一種記法。
"""

import argparse
import json
import re
import sys
from pathlib import Path

R_PAIR = "一份樣板由骨架與範例兩個檔組成"
R_PATH = "骨架與範例照固定路徑命名"
R_FILLED = "範例是骨架填完填位符號的樣子"
RULES = [R_PAIR, R_PATH, R_FILLED]  # 3 條的強度都是 must
SOURCE = "樣板-格式規範.md"

EXAMPLE_NAME = re.compile(r"^(.+)\.example\.([^.]+)$")
SKELETON_NAME = re.compile(r"^(.+)\.([^.]+)$")
PLACEHOLDER = re.compile(r"\{\{(.+?)\}\}")


def line_pattern(line: str) -> re.Pattern[str]:
    """把骨架的一行變成比對用的樣式:固定的字照原樣,填位符號可以換成任何內容。"""
    parts = PLACEHOLDER.split(line.strip())
    body = "".join(re.escape(part) if index % 2 == 0 else ".*?" for index, part in enumerate(parts))
    return re.compile(f"^{body}$")


def read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        print(f"錯誤: {path} 不是 UTF-8 編碼。請把它轉存成 UTF-8 再執行。", file=sys.stderr)
        sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", required=True, type=Path, help="目標 skill 的根目錄(含 SKILL.md 的那一層)")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not (args.skill / "SKILL.md").is_file():
        print(f"錯誤: {args.skill} 底下沒有 SKILL.md。--skill 要給 skill 的根目錄(含 SKILL.md 的那一層)。", file=sys.stderr)
        return 2

    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}
    candidates: list[dict] = []
    pairs: list[tuple[Path, Path]] = []

    def bad(rule: str, path: Path, reason: str, line: int = 0, text: str = "") -> None:
        violations[rule].append({"file": path.relative_to(args.skill).as_posix(), "line": line, "text": text, "reason": reason})

    templates_dir = args.skill / "templates"
    entries = sorted(p for p in templates_dir.rglob("*") if p.is_file() and not p.name.startswith(".")) if templates_dir.is_dir() else []
    top = [p for p in entries if p.parent == templates_dir]
    for path in entries:
        if path.parent != templates_dir:
            bad(R_PATH, path, "樣板要直接放在 `templates/` 底下,不放進子目錄")

    names = {p.name for p in top}
    for path in top:
        example_match = EXAMPLE_NAME.match(path.name)
        if example_match:
            skeleton_name = f"{example_match.group(1)}.{example_match.group(2)}"
            if skeleton_name not in names:
                bad(R_PAIR, path, f"找不到這份範例的骨架 `templates/{skeleton_name}`")
            continue
        if path.name.endswith(".example") or ".example." in path.name:
            bad(R_PATH, path, "範例要命名成 `<樣板名字>.example.<格式>`:`.example` 夾在名字與副檔名之間,檔名以 `<格式>` 結尾")
            continue
        skeleton_match = SKELETON_NAME.match(path.name)
        if not skeleton_match:
            bad(R_PATH, path, "樣板的檔名要有副檔名:`<樣板名字>.<格式>`")
            continue
        example_name = f"{skeleton_match.group(1)}.example.{skeleton_match.group(2)}"
        if example_name not in names:
            # 範例只是命名錯了的,已經在〈骨架與範例照固定路徑命名〉報過,不再報一次缺範例
            if not any(other.startswith(f"{path.name}.") and other.endswith(".example") for other in names):
                bad(R_PAIR, path, f"這份骨架沒有範例 `templates/{example_name}`")
            continue
        pairs.append((path, templates_dir / example_name))

    compared = 0
    weak = 0
    for skeleton, example in pairs:
        skeleton_lines = [(number, line) for number, line in enumerate(read_lines(skeleton), start=1) if line.strip()]
        example_lines = [(number, line) for number, line in enumerate(read_lines(example), start=1) if line.strip()]
        if not any(PLACEHOLDER.search(line) for _, line in skeleton_lines):
            candidates.append(
                {
                    "rule": "會變動的地方用填位符號標出",
                    "file": skeleton.relative_to(args.skill).as_posix(),
                    "line": 0,
                    "text": "",
                    "reason": "骨架裡找不到 `{{名稱}}`;腳本沒有比對這一份的範例,請判斷它是沒有標出會變動的地方,還是用了別種記法",
                }
            )
            continue
        compared += 1
        wildcard = [(number, line) for number, line in skeleton_lines if not PLACEHOLDER.sub("", line).strip()]
        if wildcard:
            weak += 1
            candidates.append(
                {
                    "rule": R_FILLED,
                    "file": skeleton.relative_to(args.skill).as_posix(),
                    "line": wildcard[0][0],
                    "text": wildcard[0][1].strip(),
                    "reason": f"骨架有 {len(wildcard)} 行整行只有填位符號,範例的任何一行都對得上它;這一份的逐行比對沒有鑑別力,請自己對照範例有沒有多出骨架沒有的內容",
                }
            )
        patterns = [line_pattern(line) for _, line in skeleton_lines]
        for number, line in example_lines:
            if PLACEHOLDER.search(line):
                bad(R_FILLED, example, "範例還留著填位符號 `{{…}}`;每個填位符號都要換成具體內容", number, line.strip())
            elif not any(pattern.match(line.strip()) for pattern in patterns):
                bad(R_FILLED, example, "這一行對不回骨架的任何一行:骨架沒有這一行,或骨架裡固定的字被改了", number, line.strip())

    total = len(pairs)
    passed_evidence = {
        R_PAIR: f"{total} 份樣板的骨架與範例都成對" if top else "`templates/` 底下沒有樣板",
        R_PATH: f"{len(top)} 個檔都直接放在 `templates/` 底下,範例只在副檔名之前多一段 `.example`" if top else "`templates/` 底下沒有樣板",
        R_FILLED: (
            f"{compared} 份範例都沒有殘留填位符號,每一行都對得回骨架"
            + (f";其中 {weak} 份的骨架有整行只有填位符號的行,逐行比對沒有鑑別力" if weak else "")
            if compared
            else "沒有可以比對的樣板"
        ),
    }
    checks = []
    for rule in RULES:
        mine = violations[rule]
        checks.append(
            {
                "rule": rule,
                "source": SOURCE,
                "strength": "must",
                "result": "不過" if mine else "過",
                "evidence": ";".join(f"{v['file']}" + (f" 第 {v['line']} 行" if v["line"] else "") + f":{v['reason']}" for v in mine) if mine else passed_evidence[rule],
                "violations": mine,
            }
        )
    passed = not any(violations.values())
    report = {
        "skill": str(args.skill),
        "passed": passed,
        "templates": [
            {"skeleton": s.relative_to(args.skill).as_posix(), "example": e.relative_to(args.skill).as_posix()} for s, e in pairs
        ],
        "checks": checks,
        "candidates": candidates,
    }
    print(f"檢查了 {total} 份樣板,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
