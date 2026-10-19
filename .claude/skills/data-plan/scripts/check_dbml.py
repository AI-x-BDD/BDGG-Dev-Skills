# /// script
# requires-python = ">=3.10"
# dependencies = ["pydbml>=1.1,<2"]
# ///
"""驗證 data-plan 交出的 DBML 檔。

檢查項目:pydbml 解析得了(語法正確、Ref 兩端的表與欄位都存在)、每張表都有 `需求:` 開頭的 Note、
plan.md 這一步端點的需求出處都對得到表、表 Note 的需求編號都在 spec.md 裡。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

from pydbml import PyDBML

ENDPOINT_ROW = re.compile(r"^\| E(\d+) \|(.*)\|$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")  # Markdown 表格裡跳脫的 \| 是內容,不是欄分隔
WAVE_ROW = re.compile(r"^\| (\d+) \| S(\d+) \| E(\d+) ")
RANGE = re.compile(r"\b(FR|NFR|SC)-(\d+)\s*[–—~]\s*(?:(?:FR|NFR|SC)-)?(\d+)\b")
REQUIREMENT_ID = re.compile(r"\b((?:FR|NFR|SC)-\d+)\b")

R_PARSE = "pydbml 解析得了"
R_TAGGED = "每張表都有需求 Note"
R_COVERAGE = "plan.md 這一步的需求出處都對得到表"
R_SOURCES = "表 Note 的需求編號都在 spec.md 裡"
RULES = [R_PARSE, R_TAGGED, R_COVERAGE, R_SOURCES]


def section(lines: list[str], heading: str) -> list[str]:
    """取出某個標題底下、到下一個同級或更高標題之前的行。"""
    level = len(heading) - len(heading.lstrip("#"))
    inside, picked = False, []
    for line in lines:
        if line.startswith("#") and not line.startswith("#" * (level + 1)):
            inside = line.strip() == heading
            continue
        if inside:
            picked.append(line)
    return picked


def requirement_ids(text: str) -> set[str]:
    """取出一段文字裡的需求編號,`FR-001–FR-019` 這類範圍展開成每一個編號。"""
    ids = set(REQUIREMENT_ID.findall(text))
    for kind, start, end in RANGE.findall(text):
        ids |= {f"{kind}-{n:0{len(start)}d}" for n in range(int(start), int(end) + 1)}
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dbml", required=True, type=Path, help="contracts/schema.dbml 的路徑")
    parser.add_argument("--plan", required=True, type=Path, help="system-analysis 產出的 plan.md 路徑,用來找這一步分析的端點與需求出處")
    parser.add_argument("--spec", required=True, type=Path, help="spec.md 的路徑,用來確認需求編號都有定義")
    parser.add_argument("--step", required=True, help="這份 DBML 對應的波段表步驟編號,例如 S4")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    step_match = re.fullmatch(r"S?(\d+)", args.step.strip())
    if not step_match:
        print(f"錯誤: --step 收到「{args.step}」,要給波段表的步驟編號,例如 S4。", file=sys.stderr)
        return 2
    step = int(step_match.group(1))
    for path in (args.dbml, args.plan, args.spec):
        if not path.is_file():
            print(f"錯誤: 找不到 {path};--dbml、--plan、--spec 都要給檔案路徑。", file=sys.stderr)
            return 2

    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}

    def bad(rule: str, where: str, reason: str) -> None:
        violations[rule].append({"where": where, "reason": reason})

    tables = []
    try:
        tables = PyDBML(args.dbml.read_text(encoding="utf-8")).tables
    except Exception as exc:  # pydbml 的語法與參照錯誤種類很多,一律轉成不符項
        bad(R_PARSE, str(args.dbml), f"{type(exc).__name__}: {exc}")

    tagged: set[str] = set()
    for table in tables:
        note = (table.note.text if table.note else "").strip()
        if not note.startswith("需求:"):
            bad(R_TAGGED, f"Table {table.name}", "沒有 `Note: '需求: …'`")
            continue
        ids = requirement_ids(note)
        if not ids:
            bad(R_TAGGED, f"Table {table.name}", "需求 Note 裡沒有任何需求編號")
        tagged |= ids

    plan_lines = args.plan.read_text(encoding="utf-8").splitlines()
    endpoint = next((int(m.group(3)) for l in section(plan_lines, "### 分析波段") if (m := WAVE_ROW.match(l.strip())) and int(m.group(2)) == step), None)
    needed: set[str] = set()
    if endpoint is None:
        bad(R_COVERAGE, "plan.md", f"`### 分析波段` 沒有 S{step}")
    else:
        row = next((m.group(2) for l in section(plan_lines, "### 端點盤點") if (m := ENDPOINT_ROW.match(l.strip())) and int(m.group(1)) == endpoint), None)
        if row is None:
            bad(R_COVERAGE, "plan.md", f"S{step} 分析的 E{endpoint} 不在 `### 端點盤點`")
        else:
            needed = requirement_ids(CELL_SPLIT.split(row)[-1])
    if tables:
        for rid in sorted(needed - tagged):
            bad(R_COVERAGE, rid, f"E{endpoint} 的需求出處 {rid} 沒有任何一張表的 Note 對到")

    defined = set(re.findall(r"\*\*((?:FR|NFR|SC)-\d+)\*\*", args.spec.read_text(encoding="utf-8")))
    for rid in sorted(tagged - defined):
        bad(R_SOURCES, rid, f"{rid} 在 spec.md 裡沒有定義")

    parse_failed = bool(violations[R_PARSE])
    passed_evidence = {
        R_PARSE: f"解析出 {len(tables)} 張表,Ref 兩端都存在",
        R_TAGGED: f"{len(tables)} 張表都有需求 Note",
        R_COVERAGE: f"S{step}(E{endpoint})的 {len(needed)} 個需求出處都對得到表",
        R_SOURCES: f"表 Note 的 {len(tagged)} 個需求編號都在 spec.md 裡",
    }
    checks = []
    for rule in RULES:
        mine = violations[rule]
        skipped = parse_failed and rule in (R_TAGGED, R_COVERAGE, R_SOURCES) and not mine
        result = "略過" if skipped else ("不過" if mine else "過")
        evidence = "解析失敗,沒有表可以檢查" if skipped else (";".join(f"{v['where']}:{v['reason']}" for v in mine) if mine else passed_evidence[rule])
        checks.append({"rule": rule, "result": result, "evidence": evidence, "violations": mine})
    passed = not any(violations.values())
    report = {"dbml": str(args.dbml), "step": f"S{step}", "passed": passed, "checks": checks}
    print(f"檢查了 {len(tables)} 張表、{len(needed)} 個需求出處,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
