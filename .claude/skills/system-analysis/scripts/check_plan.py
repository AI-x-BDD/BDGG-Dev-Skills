# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查一份 plan.md 的分析流程規劃是否前後一致。

檢查項目:端點從 E1 連號且個數和敘述一致、每個端點在波段表恰好出現一次、步驟與 wave 的編號、
「平行」欄和同一波的步驟一致、結尾的總數、Documentation 樹裡每一步恰好一份產出,
以及(給了 --spec 時)需求出處的編號都在 spec.md 裡。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

ENDPOINT_ROW = re.compile(r"^\| E(\d+) \|(.*)\|$")
ENDPOINT_COUNT = re.compile(r"這次需求涉及 (\d+) 個端點")
WAVE_ROW = re.compile(r"^\| (\d+) \| S(\d+) \| E(\d+) [^|]+\| ([^|]+) \|.*\|$")
PARALLEL = re.compile(r"^✅ 與 (S\d+(?:、S\d+)*) 平行$")
SUMMARY = re.compile(r"共 (\d+) 個 wave、(\d+) 個步驟")
DOC_OUTPUT = re.compile(r"# S(\d+) 產出[((]E(\d+)")
REQUIREMENT_ID = re.compile(r"\b((?:FR|NFR|SC)-\d+)\b")

R_ENDPOINTS = "端點從 E1 連號且個數和敘述一致"
R_ONCE = "每個端點在波段表恰好出現一次"
R_NUMBERING = "步驟從 S1 連號,wave 從 1 起不遞減不跳號"
R_PARALLEL = "「平行」欄和同一波的其他步驟一致"
R_SUMMARY = "結尾的 wave 數與步驟數和波段表一致"
R_OUTPUTS = "每一步在 Documentation 樹恰好產出一份檔且端點一致"
R_SOURCES = "需求出處的編號都在 spec.md 裡"
RULES = [R_ENDPOINTS, R_ONCE, R_NUMBERING, R_PARALLEL, R_SUMMARY, R_OUTPUTS, R_SOURCES]


def section(lines: list[tuple[int, str]], heading: str) -> list[tuple[int, str]]:
    """取出某個標題底下、到下一個同級或更高標題之前的行。"""
    level = len(heading) - len(heading.lstrip("#"))
    inside, picked = False, []
    for number, line in lines:
        if line.startswith("#") and not line.startswith("#" * (level + 1)):
            inside = line.strip() == heading
            continue
        if inside:
            picked.append((number, line))
    return picked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plan", required=True, type=Path, help="plan.md 的路徑")
    parser.add_argument("--spec", type=Path, help="spec.md 的路徑;給了才檢查需求出處的編號")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    for path in [args.plan] + ([args.spec] if args.spec else []):
        if not path.is_file():
            print(f"錯誤: 找不到 {path}。", file=sys.stderr)
            return 2

    lines = list(enumerate(args.plan.read_text(encoding="utf-8").splitlines(), start=1))
    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}

    def bad(rule: str, reason: str, line: int = 0, text: str = "") -> None:
        violations[rule].append({"line": line, "text": text, "reason": reason})

    # 端點盤點
    inventory = section(lines, "### 端點盤點")
    endpoints = [(n, int(m.group(1)), m.group(2)) for n, l in inventory if (m := ENDPOINT_ROW.match(l.strip()))]
    if not endpoints:
        bad(R_ENDPOINTS, "`### 端點盤點` 底下找不到 `| E<序號> |` 開頭的列")
    for expected, (number, actual, _) in enumerate(endpoints, start=1):
        if actual != expected:
            bad(R_ENDPOINTS, f"第 {expected} 列的端點是 E{actual},要從 E1 連號", number)
    count = next(((n, int(m.group(1))) for n, l in inventory if (m := ENDPOINT_COUNT.search(l))), None)
    if count is None:
        bad(R_ENDPOINTS, "找不到「這次需求涉及 N 個端點」")
    elif count[1] != len(endpoints):
        bad(R_ENDPOINTS, f"敘述寫 {count[1]} 個端點,表裡有 {len(endpoints)} 列", count[0])
    endpoint_ids = {e for _, e, _ in endpoints}

    # 分析波段
    waves_section = section(lines, "### 分析波段")
    rows = [(n, int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4).strip()) for n, l in waves_section if (m := WAVE_ROW.match(l.strip()))]
    if not rows:
        bad(R_NUMBERING, "`### 分析波段` 底下找不到 `| <wave> | S<序號> | E<序號> … |` 的列")

    seen: dict[int, int] = {}
    for number, _, step, endpoint, _ in rows:
        if endpoint not in endpoint_ids:
            bad(R_ONCE, f"S{step} 分析的 E{endpoint} 不在端點盤點裡", number)
        seen[endpoint] = seen.get(endpoint, 0) + 1
    for endpoint in sorted(endpoint_ids):
        if seen.get(endpoint, 0) != 1:
            bad(R_ONCE, f"E{endpoint} 在波段表出現 {seen.get(endpoint, 0)} 次,要恰好 1 次")

    previous_wave = 0
    for expected, (number, wave, step, _, _) in enumerate(rows, start=1):
        if step != expected:
            bad(R_NUMBERING, f"第 {expected} 列的步驟是 S{step},要從 S1 連號", number)
        if wave < previous_wave:
            bad(R_NUMBERING, f"S{step} 的 wave {wave} 比上一列的 {previous_wave} 小", number)
        elif wave > previous_wave + 1:
            bad(R_NUMBERING, f"S{step} 從 wave {previous_wave} 跳到 {wave}", number)
        previous_wave = max(previous_wave, wave)

    by_wave: dict[int, set[int]] = {}
    for _, wave, step, _, _ in rows:
        by_wave.setdefault(wave, set()).add(step)
    for number, wave, step, _, cell in rows:
        others = by_wave[wave] - {step}
        match = PARALLEL.match(cell)
        if cell == "—":
            if others:
                bad(R_PARALLEL, f"S{step} 寫「—」,但同一波還有 {'、'.join(f'S{s}' for s in sorted(others))}", number, cell)
        elif match:
            named = {int(s[1:]) for s in match.group(1).split("、")}
            if named != others:
                expect = "、".join(f"S{s}" for s in sorted(others)) or "沒有其他步驟,要寫「—」"
                bad(R_PARALLEL, f"S{step} 點名的平行步驟和同一波不一致;同一波的其他步驟是 {expect}", number, cell)
        else:
            bad(R_PARALLEL, "「平行」欄要寫成「✅ 與 S<序號>、S<序號> 平行」或「—」", number, cell)

    summary = next(((n, int(m.group(1)), int(m.group(2))) for n, l in waves_section if (m := SUMMARY.search(l))), None)
    if summary is None:
        bad(R_SUMMARY, "找不到「共 W 個 wave、M 個步驟」")
    else:
        if summary[1] != len(by_wave):
            bad(R_SUMMARY, f"結尾寫 {summary[1]} 個 wave,波段表有 {len(by_wave)} 個", summary[0])
        if summary[2] != len(rows):
            bad(R_SUMMARY, f"結尾寫 {summary[2]} 個步驟,波段表有 {len(rows)} 個", summary[0])

    # Documentation 樹
    step_endpoint = {step: endpoint for _, _, step, endpoint, _ in rows}
    outputs: dict[int, list[tuple[int, int]]] = {}
    for number, line in section(lines, "### Documentation (this feature)"):
        for m in DOC_OUTPUT.finditer(line):
            outputs.setdefault(int(m.group(1)), []).append((number, int(m.group(2))))
    for step, endpoint in step_endpoint.items():
        found = outputs.get(step, [])
        if len(found) != 1:
            bad(R_OUTPUTS, f"S{step} 在 Documentation 樹有 {len(found)} 份產出,要恰好 1 份")
        elif found[0][1] != endpoint:
            bad(R_OUTPUTS, f"S{step} 的產出標成 E{found[0][1]},波段表是 E{endpoint}", found[0][0])
    for step in sorted(set(outputs) - set(step_endpoint)):
        bad(R_OUTPUTS, f"Documentation 樹有 S{step} 的產出,但波段表沒有 S{step}", outputs[step][0][0])

    # 需求出處
    skipped = args.spec is None
    if not skipped:
        defined = set(re.findall(r"\*\*((?:FR|NFR|SC)-\d+)\*\*", args.spec.read_text(encoding="utf-8")))
        for number, endpoint, row in endpoints:
            source = row.split("|")[-1]
            for rid in REQUIREMENT_ID.findall(source):
                if rid not in defined:
                    bad(R_SOURCES, f"E{endpoint} 的需求出處 {rid} 在 spec.md 裡沒有定義", number, rid)

    passed_evidence = {
        R_ENDPOINTS: f"E1–E{len(endpoints)} 連號,和「涉及 {len(endpoints)} 個端點」一致",
        R_ONCE: f"{len(endpoint_ids)} 個端點在波段表各出現 1 次",
        R_NUMBERING: f"S1–S{len(rows)} 連號,wave 1–{len(by_wave)} 不遞減不跳號",
        R_PARALLEL: f"{len(rows)} 列的「平行」欄都和同一波的步驟一致",
        R_SUMMARY: f"結尾的 {len(by_wave)} 個 wave、{len(rows)} 個步驟和波段表一致",
        R_OUTPUTS: f"{len(rows)} 個步驟在 Documentation 樹各有 1 份產出,端點一致",
        R_SOURCES: "沒有給 --spec,沒有檢查" if skipped else "需求出處的編號都在 spec.md 裡有定義",
    }
    checks = []
    for rule in RULES:
        mine = violations[rule]
        checks.append(
            {
                "rule": rule,
                "result": "略過" if rule == R_SOURCES and skipped else ("不過" if mine else "過"),
                "evidence": ";".join((f"第 {v['line']} 行:" if v["line"] else "") + v["reason"] for v in mine) if mine else passed_evidence[rule],
                "violations": mine,
            }
        )
    passed = not any(violations.values())
    report = {"plan": str(args.plan), "spec": str(args.spec) if args.spec else None, "passed": passed, "checks": checks}
    print(f"檢查了 {len(endpoints)} 個端點、{len(rows)} 個步驟,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
