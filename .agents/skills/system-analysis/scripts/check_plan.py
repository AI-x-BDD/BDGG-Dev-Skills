# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查一份 plan.md 的分析流程規劃是否前後一致。

檢查項目:端點從 E1 連號且個數和敘述一致、每個端點在波段表恰好出現一次、步驟與 wave 的編號、
「Planner」欄只有四支 planner 或「無合適的 planner」、「平行」欄和同一波的步驟一致、結尾的總數、
Documentation 樹裡每一支指派的 planner 都有產出且步驟、端點與檔案種類對得上、同一波不共用產出路徑、
「待決問題」表的編號與步驟都存在(「提出的步驟」可以是 S<步驟>、tasks 或 implement T<編號>)、
Documentation 樹列出的產出檔裡引用的待決問題都登記在表裡,以及(給了 --spec 時)需求出處的編號都在 spec.md 裡。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

ENDPOINT_ROW = re.compile(r"^\| E(\d+) \|(.*)\|$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")  # Markdown 表格裡跳脫的 \| 是內容,不是欄分隔
ENDPOINT_COUNT = re.compile(r"這次需求涉及 (\d+) 個端點")
WAVE_ROW = re.compile(r"^\| (\d+) \| S(\d+) \| E(\d+) (?:\\.|[^|\\])+\| ((?:\\.|[^|\\])+) \| ((?:\\.|[^|\\])+) \|.*\|$")
PARALLEL = re.compile(r"^✅ 與 (S\d+(?:、S\d+)*) 平行$")
SUMMARY = re.compile(r"共 (\d+) 個 wave、(\d+) 個步驟")
DOC_OUTPUT = re.compile(r"^(\s*)[├└]── (\S+)\s+# (S\d+(?:、S\d+)*) 產出[((](.+?)[,,]\s*([a-z]+-plan)[))]")
QUESTION_ROW = re.compile(r"^\| Q(\d+) \| (?:S(\d+)|tasks|implement T\d+) \|(.*)\|((?:\\.|[^|\\])*)\|((?:\\.|[^|\\])*)\|$")
QUESTION_REF = re.compile(r"待決問題\s*(Q\d+(?:\s*(?:[–-]\s*Q?\d+|[、,,和與及]\s*Q\d+))*)?")
PLANNERS = {"ui-plan", "data-plan", "api-plan", "deploy-plan"}
NO_PLANNER = "無合適的 planner"
PLANNER_PATHS = {
    "ui-plan": ("prototype 開頭的資料夾", lambda path: re.fullmatch(r"prototype(-[\w-]+)?/", path) is not None),
    "deploy-plan": ("deploy/", lambda path: path == "deploy/"),
    "api-plan": ("contracts/ 底下的 .openapi.yaml 或 .asyncapi.yaml", lambda path: path.startswith("contracts/") and path.endswith((".openapi.yaml", ".asyncapi.yaml"))),
    "data-plan": ("contracts/ 底下的 .dbml", lambda path: path.startswith("contracts/") and path.endswith(".dbml")),
}
REQUIREMENT_ID = re.compile(r"\b((?:FR|NFR|SC)-\d+)\b")

R_ENDPOINTS = "端點從 E1 連號且個數和敘述一致"
R_ONCE = "每個端點在波段表恰好出現一次"
R_NUMBERING = "步驟從 S1 連號,wave 從 1 起不遞減不跳號"
R_PLANNER = "「Planner」欄只有四支 planner 或「無合適的 planner」"
R_PARALLEL = "「平行」欄和同一波的其他步驟一致"
R_SUMMARY = "結尾的 wave 數與步驟數和波段表一致"
R_OUTPUTS = "每支指派的 planner 在 Documentation 樹都有產出且對得上"
R_QUESTIONS = "「待決問題」表的編號與步驟都存在"
R_REFERENCES = "規格檔引用的待決問題都登記在表裡"
R_SOURCES = "需求出處的編號都在 spec.md 裡"
RULES = [R_ENDPOINTS, R_ONCE, R_NUMBERING, R_PLANNER, R_PARALLEL, R_SUMMARY, R_OUTPUTS, R_QUESTIONS, R_REFERENCES, R_SOURCES]


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
    rows = [(n, int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(5).strip()) for n, l in waves_section if (m := WAVE_ROW.match(l.strip()))]
    planners: dict[int, list[str]] = {}
    for n, l in waves_section:
        if m := WAVE_ROW.match(l.strip()):
            names = [x.strip() for x in m.group(4).split("、")]
            planners[int(m.group(2))] = names
            if names != [NO_PLANNER] and not all(x in PLANNERS for x in names):
                bad(R_PLANNER, f"S{m.group(2)} 的 Planner 欄是「{m.group(4).strip()}」;要是 {'、'.join(sorted(PLANNERS))} 之一(多支用、分隔),或「{NO_PLANNER}」", n)
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
    step_wave = {step: wave for _, wave, step, _, _ in rows}
    produced: set[tuple[int, str]] = set()
    path_steps: dict[str, set[int]] = {}
    for number, line in section(lines, "### Documentation (this feature)"):
        m = DOC_OUTPUT.match(line)
        if not m:
            continue
        indent, name, steps_text, endpoints_text, planner = m.groups()
        path = ("contracts/" + name) if indent else name
        line_endpoints = {int(e) for e in re.findall(r"E(\d+)", endpoints_text)}
        ok, expect = PLANNER_PATHS.get(planner, ("", lambda _: False))[1](path), PLANNER_PATHS.get(planner, ("四支 planner 之一",))[0]
        if not ok:
            bad(R_OUTPUTS, f"{path} 標成 {planner} 的產出,但 {planner} 的產出要是 {expect}", number)
        for step in (int(x[1:]) for x in steps_text.split("、")):
            if step not in step_endpoint:
                bad(R_OUTPUTS, f"Documentation 樹有 S{step} 的產出,但波段表沒有 S{step}", number)
                continue
            if step_endpoint[step] not in line_endpoints:
                bad(R_OUTPUTS, f"{path} 標了 S{step},但沒有標 S{step} 分析的 E{step_endpoint[step]}", number)
            if planner not in planners.get(step, []):
                bad(R_OUTPUTS, f"{path} 標成 S{step} 的 {planner} 產出,但 S{step} 的 Planner 欄沒有 {planner}", number)
            produced.add((step, planner))
            path_steps.setdefault(path, set()).add(step)
    for step, names in planners.items():
        for name in names:
            if name in PLANNERS and (step, name) not in produced:
                bad(R_OUTPUTS, f"S{step} 指派了 {name},但 Documentation 樹沒有它的產出")
        if names == [NO_PLANNER] and any(s == step for s, _ in produced):
            bad(R_OUTPUTS, f"S{step} 是「{NO_PLANNER}」,Documentation 樹卻列了它的產出")
    for path, steps in path_steps.items():
        waves: dict[int, list[int]] = {}
        for step in steps:
            waves.setdefault(step_wave.get(step, 0), []).append(step)
        for wave, same in waves.items():
            if len(same) > 1:
                bad(R_OUTPUTS, f"{path} 由同一波(wave {wave})的 {'、'.join(f'S{x}' for x in sorted(same))} 一起寫,平行的 sub agent 會互相覆蓋")

    # 待決問題
    question_rows = [(n, l.strip()) for n, l in section(lines, "## 待決問題") if re.match(r"\| Q\d", l.strip())]
    for expected, (number, line) in enumerate(question_rows, start=1):
        m = QUESTION_ROW.match(line)
        if not m:
            bad(R_QUESTIONS, "列要寫成「| Q<序號> | S<步驟>、tasks 或 implement T<編號> | 問題 | 擋住 | 決定 |」", number, line)
            continue
        if int(m.group(1)) != expected:
            bad(R_QUESTIONS, f"第 {expected} 列是 Q{m.group(1)},要從 Q1 連號", number)
        if m.group(2) and int(m.group(2)) not in step_endpoint:
            bad(R_QUESTIONS, f"Q{m.group(1)} 的提出步驟 S{m.group(2)} 不在波段表", number)
        blocked = m.group(4).strip()
        if blocked != "—":
            for step in re.findall(r"S(\d+)", blocked) or ["?"]:
                if not step.isdigit() or int(step) not in step_endpoint:
                    bad(R_QUESTIONS, f"Q{m.group(1)} 的「擋住」欄是「{blocked}」,要是波段表裡的步驟或「—」", number)
        if not m.group(5).strip():
            bad(R_QUESTIONS, f"Q{m.group(1)} 的「決定」欄是空的,還沒決定要寫「待決」", number)

    # 規格檔引用的待決問題
    registered = {int(m.group(1)) for _, l in question_rows if (m := QUESTION_ROW.match(l))}
    raised = {int(m.group(2)) for _, l in question_rows if (m := QUESTION_ROW.match(l)) and m.group(2)}
    scanned = 0
    for output, steps in sorted(path_steps.items()):
        target = args.plan.parent / output
        files = sorted(f for f in target.rglob("*") if f.is_file()) if target.is_dir() else ([target] if target.is_file() else [])
        for file in files:
            try:
                text = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            scanned += 1
            name = file.relative_to(args.plan.parent).as_posix()
            unnumbered = []
            for number, line in enumerate(text.splitlines(), start=1):
                for ref in QUESTION_REF.finditer(line):
                    if not ref.group(1):
                        unnumbered.append(number)
                        continue
                    for a, b in re.findall(r"Q(\d+)(?:\s*[–-]\s*Q?(\d+))?", ref.group(1)):
                        for q in range(int(a), int(b or a) + 1):
                            if q not in registered:
                                bad(R_REFERENCES, f"{name} 第 {number} 行引用待決問題 Q{q},表裡沒有這一題")
            if unnumbered and not steps & raised:
                owners = "、".join(f"S{s}" for s in sorted(steps))
                where = "、".join(str(n) for n in unnumbered)
                bad(R_REFERENCES, f"{name} 第 {where} 行寫了待決問題但沒有 Q 號,表裡沒有任何一列是 {owners} 提出的")

    # 需求出處
    skipped = args.spec is None
    if not skipped:
        defined = set(re.findall(r"\*\*((?:FR|NFR|SC)-\d+)\*\*", args.spec.read_text(encoding="utf-8")))
        for number, endpoint, row in endpoints:
            source = CELL_SPLIT.split(row)[-1]
            for rid in REQUIREMENT_ID.findall(source):
                if rid not in defined:
                    bad(R_SOURCES, f"E{endpoint} 的需求出處 {rid} 在 spec.md 裡沒有定義", number, rid)

    passed_evidence = {
        R_ENDPOINTS: f"E1–E{len(endpoints)} 連號,和「涉及 {len(endpoints)} 個端點」一致",
        R_ONCE: f"{len(endpoint_ids)} 個端點在波段表各出現 1 次",
        R_NUMBERING: f"S1–S{len(rows)} 連號,wave 1–{len(by_wave)} 不遞減不跳號",
        R_PLANNER: f"{len(rows)} 列的「Planner」欄都是四支 planner 或「{NO_PLANNER}」",
        R_PARALLEL: f"{len(rows)} 列的「平行」欄都和同一波的步驟一致",
        R_SUMMARY: f"結尾的 {len(by_wave)} 個 wave、{len(rows)} 個步驟和波段表一致",
        R_OUTPUTS: f"{len(produced)} 個步驟與 planner 的組合在 Documentation 樹都有產出,步驟、端點與檔案種類對得上",
        R_QUESTIONS: f"「待決問題」表的 {len(question_rows)} 列編號與步驟都存在",
        R_REFERENCES: f"Documentation 樹列出的 {scanned} 個產出檔裡引用的待決問題都登記在表裡",
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
