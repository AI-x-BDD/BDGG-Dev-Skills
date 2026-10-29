# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查一份 analysis.md 的輪次、問題編號、欄位值、位置與判定。

檢查項目:
  輪次連號      「## 第 N 輪」從 1 起連號
  編號連續      問題表的編號從 A1 起跨輪連續、不重複
  欄位值        類別、嚴重度、狀態只用規定的值;「回哪一步」的每一支都是 SDD 流程裡的 Skill
  位置          每個問題至少兩處位置,每一處以 `檔案` 開頭,而且那個檔存在
                (constitution/ 開頭的相對於專案根目錄,其餘相對於 analysis.md 所在的 spec package)
  上一輪列齊    第 2 輪起,前幾輪還沒解決的問題都列在「上一輪的問題」表,表上的編號都存在
  判定一致      判定寫的是最後一輪;✅ / ⛔ 與算出來的未解決 CRITICAL、HIGH 一致
  空段落省略    每一輪裡的表格段落至少有一列內容;沒有內容的段落整節省略,不寫空表或「無」
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

CATEGORIES = {"憲法", "矛盾", "遺漏", "無法實作", "無法追溯"}
SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
BLOCKING = {"CRITICAL", "HIGH"}
STATUSES = {"✅ 已修正", "✅ 已澄清", "❌ 仍存在"}
SKILLS = {
    "/specify", "/clarify-over-specs", "/technical-research", "/system-analysis", "/api-plan",
    "/data-plan", "/ui-plan", "/deploy-plan", "/tasks", "/constitution",
}

VERDICT = re.compile(r"^\*\*最新一輪:第 (\d+) 輪\((.+?)\)— (✅ 可以進 `/implement`|⛔ 不能進 `/implement`)\*\*$")
ROUND = re.compile(r"^## 第 (\d+) 輪\((.+?)\)$")
ISSUE_ID = re.compile(r"^A(\d+)$")
LOCATION = re.compile(r"^`([^`]+)`")

R_ROUNDS = "輪次從 1 起連號"
R_IDS = "問題編號從 A1 起跨輪連續、不重複"
R_VALUES = "類別、嚴重度、狀態與回哪一步只用規定的值"
R_LOCATIONS = "每個問題至少兩處位置,而且檔案存在"
R_CARRY = "前幾輪還沒解決的問題都列在上一輪的問題表"
R_VERDICT = "判定與最後一輪的未解決 CRITICAL、HIGH 一致"
R_EMPTY = "沒有內容的段落整節省略"
RULES = [R_ROUNDS, R_IDS, R_VALUES, R_LOCATIONS, R_CARRY, R_VERDICT, R_EMPTY]
LIST_SECTIONS = {"修正順序"}
EMPTY_MARKS = {"無", "(無)", "—", "-"}


def cells(line: str) -> list[str]:
    """把一列 Markdown 表格切成欄位;分隔列與非表格列回傳空清單。"""
    text = line.strip()
    if not text.startswith("|") or re.fullmatch(r"\|[\s\-|:]+\|", text):
        return []
    return [cell.strip() for cell in text.strip("|").split("|")]


def parse(lines: list[str]) -> tuple[dict | None, list[dict]]:
    """回傳判定那一行與每一輪的內容(問題表、上一輪的問題表)。"""
    verdict = None
    rounds: list[dict] = []
    section = None
    for number, line in enumerate(lines, start=1):
        text = line.strip()
        matched = VERDICT.match(text)
        if matched and verdict is None:
            verdict = {"line": number, "round": int(matched.group(1)), "blocked": matched.group(3).startswith("⛔"), "text": text}
            continue
        matched = ROUND.match(text)
        if matched:
            rounds.append({"line": number, "round": int(matched.group(1)), "issues": [], "carried": [], "sections": []})
            section = None
            continue
        if text.startswith("## "):
            section = None
            continue
        if text.startswith("### "):
            title = text[4:].strip()
            section = "issues" if title in ("問題", "新問題") else "carried" if title == "上一輪的問題" else None
            if rounds:
                rounds[-1]["sections"].append({"line": number, "title": title, "header": None, "rows": []})
            continue
        if not rounds or not rounds[-1]["sections"]:
            continue
        row = cells(text)
        if not row:
            continue
        current = rounds[-1]["sections"][-1]
        if current["header"] is None:
            current["header"] = row
            continue
        current["rows"].append({"line": number, "cells": row, "text": text})
        if section is not None and row[0] != "ID":
            rounds[-1][section].append({"line": number, "cells": row, "text": text})
    return verdict, rounds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--analysis", required=True, type=Path, help="要檢查的 analysis.md 檔案路徑,例如 specs/001-online-shop/analysis.md")
    parser.add_argument(
        "--root",
        type=Path,
        help="專案根目錄,也就是 constitution/ 所在的那一層;預設是 analysis.md 往上兩層(specs/<功能>/ 的上一層)",
    )
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not args.analysis.is_file():
        print(f"錯誤: 找不到 analysis.md {args.analysis};請給存在的檔案路徑。", file=sys.stderr)
        return 2
    try:
        lines = args.analysis.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        print(f"錯誤: {args.analysis} 不是 UTF-8 編碼;請轉存成 UTF-8 再執行。", file=sys.stderr)
        return 2

    package = args.analysis.resolve().parent
    root = args.root.resolve() if args.root else package.parent.parent
    verdict, rounds = parse(lines)
    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}

    def bad(rule: str, number: int, text: str, reason: str) -> None:
        violations[rule].append({"line": number, "text": text, "reason": reason})

    # 輪次從 1 起連號
    if not rounds:
        bad(R_ROUNDS, 0, "", "找不到任何「## 第 N 輪(日期)」標題")
    for index, block in enumerate(rounds, start=1):
        if block["round"] != index:
            bad(R_ROUNDS, block["line"], f"第 {block['round']} 輪", f"預期是第 {index} 輪;輪次要從 1 起連號")

    severity: dict[str, str] = {}
    open_ids: list[str] = []
    expected_next = 1
    for block in rounds:
        # 上一輪列齊、狀態的值
        carried_ids = set()
        resolved = set()
        for row in block["carried"]:
            values = row["cells"]
            if len(values) != 3:
                bad(R_VALUES, row["line"], row["text"], "上一輪的問題表要有 ID、狀態、依據 3 欄")
                continue
            item, status, _ = values
            if item in EMPTY_MARKS:
                continue
            carried_ids.add(item)
            if status not in STATUSES:
                bad(R_VALUES, row["line"], row["text"], f"狀態「{status}」要是 {'、'.join(sorted(STATUSES))} 之一")
            if ISSUE_ID.match(item) and item not in severity:
                bad(R_CARRY, row["line"], row["text"], f"{item} 沒有出現在前幾輪的問題表")
            if status.startswith("✅"):
                resolved.add(item)
        if block["round"] > 1:
            for item in open_ids:
                if item not in carried_ids:
                    bad(R_CARRY, block["line"], f"第 {block['round']} 輪", f"{item} 前幾輪還沒解決,要列在這一輪的上一輪的問題表")
        open_ids = [item for item in open_ids if item not in resolved]

        # 問題表:編號、欄位值、位置
        for row in block["issues"]:
            values = row["cells"]
            if len(values) != 6:
                bad(R_VALUES, row["line"], row["text"], "問題表要有 ID、類別、嚴重度、位置、摘要、回哪一步 6 欄")
                continue
            item, category, level, location, _, route = values
            if item in EMPTY_MARKS:
                continue
            matched = ISSUE_ID.match(item)
            if not matched or int(matched.group(1)) != expected_next:
                bad(R_IDS, row["line"], row["text"], f"預期是 A{expected_next};編號要從 A1 起跨輪連續、不重複")
            if matched:
                expected_next = int(matched.group(1)) + 1
            if category not in CATEGORIES:
                bad(R_VALUES, row["line"], row["text"], f"類別「{category}」要是 {'、'.join(sorted(CATEGORIES))} 之一")
            if level not in SEVERITIES:
                bad(R_VALUES, row["line"], row["text"], f"嚴重度「{level}」要是 CRITICAL、HIGH、MEDIUM、LOW 之一")
            for skill in (part.strip().strip("`") for part in route.split("、")):
                if skill not in SKILLS:
                    bad(R_VALUES, row["line"], row["text"], f"回哪一步的「{skill}」不是 SDD 流程裡的 Skill;要是 {'、'.join(sorted(SKILLS))} 之一")
            parts = [part.strip() for part in location.split(";") if part.strip()]
            if len(parts) < 2:
                bad(R_LOCATIONS, row["line"], row["text"], "位置至少要兩處,用;分隔:對不上的每一份產出物都要寫出來")
            for part in parts:
                path = LOCATION.match(part)
                if not path:
                    bad(R_LOCATIONS, row["line"], row["text"], f"「{part}」要以 `檔案` 開頭,寫成 `檔案` § 錨點")
                    continue
                relative = path.group(1).rstrip("/")
                base = root if relative.split("/")[0] == "constitution" else package
                if not (base / relative).exists():
                    bad(R_LOCATIONS, row["line"], row["text"], f"找不到 {relative}(以 {base} 為起點);檔名寫錯,或這份產出物不存在")
            severity[item] = level
            open_ids.append(item)

    # 沒有內容的段落整節省略
    for block in rounds:
        for part in block["sections"]:
            if part["title"] in LIST_SECTIONS:
                continue
            filled = [row for row in part["rows"] if row["cells"][0] not in EMPTY_MARKS]
            if not filled:
                bad(
                    R_EMPTY,
                    part["line"],
                    f"### {part['title']}",
                    f"第 {block['round']} 輪的「{part['title']}」沒有內容;沒有內容的段落整節省略(連標題一起拿掉),不寫空表或「無」",
                )

    # 判定與最後一輪一致
    if verdict is None:
        bad(R_VERDICT, 0, "", "找不到判定那一行:「**最新一輪:第 N 輪(日期)— ✅ 可以進 `/implement`**」或「⛔ 不能進 `/implement`」")
    elif rounds:
        if verdict["round"] != rounds[-1]["round"]:
            bad(R_VERDICT, verdict["line"], verdict["text"], f"判定寫第 {verdict['round']} 輪,最後一輪是第 {rounds[-1]['round']} 輪")
        blocking = [item for item in open_ids if severity.get(item) in BLOCKING]
        if verdict["blocked"] != bool(blocking):
            expected = f"⛔ 不能進(未解決:{'、'.join(blocking)})" if blocking else "✅ 可以進(沒有未解決的 CRITICAL、HIGH)"
            bad(R_VERDICT, verdict["line"], verdict["text"], f"判定和問題表對不上,應該是 {expected}")

    checks = [{"rule": rule, "result": "不過" if violations[rule] else "過", "violations": violations[rule]} for rule in RULES]
    passed = not any(violations.values())
    report = {
        "analysis": args.analysis.as_posix(),
        "passed": passed,
        "counts": {
            "rounds": len(rounds),
            "issues": len(severity),
            "open": open_ids,
            "open_blocking": [item for item in open_ids if severity.get(item) in BLOCKING],
        },
        "checks": checks,
    }
    print(f"檢查了 {len(rounds)} 輪、{len(severity)} 個問題,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
