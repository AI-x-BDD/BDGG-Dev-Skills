# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查 tasks.md 裡一個 phase 的勾選狀態。

任務        這個 phase 的每個任務是否都勾成 [X];任務編號可以帶一個小寫字尾(T001a、T001b,跨 repo 拆出的子任務),
            T001、T001a、T001b 是不同的任務
介面覆蓋    這個 phase 的介面覆蓋表,每一列的實作欄與測試欄寫的任務是否都勾了;
            寫的是後面 phase 的任務時,那一列列在 deferred_rows(還沒輪到),不算不過
⏸ 延後    描述開頭(在 [P]、[US1] 這類標籤之後)是 ⏸ 的未勾任務是排除或延後的任務,列在 paused_tasks,
            不算進 unchecked_tasks;覆蓋列沒勾的只有 ⏸ 任務時,那一列列在 paused_rows,不算不過
待決問題    給了 --plan 時,plan.md「待決問題」表的每一列是否寫成
            「| Q<序號> | S<步驟>、tasks 或 implement T<編號> | 問題 | 擋住 | 決定 |」;不符的列在 bad_question_rows
結果以 JSON 寫到 stdout;這個 phase 或前面 phase 有沒勾的任務、覆蓋列,或待決問題表有不符的列時 exit code 是 1,
參數或檔案有誤時是 2。
"""

import argparse
import json
import re
import sys
from pathlib import Path

PHASE = re.compile(r"^## Phase (\d+):\s*(.+?)\s*$")
TASK = re.compile(r"^- \[([ xX])\] T(\d{3}[a-z]?)\b\s*((?:\[[^\]]*\]\s*)*)(.*)$")
PAUSED = "⏸"
COVERAGE_HEADING = re.compile(r"^### 介面覆蓋[((](.+?)[))]")
COVERAGE_ROW = re.compile(r"^\| (`.+?) \| (.*?) \| (.*?) \|$")
TASK_ID = re.compile(r"T(\d{3}[a-z]?)(?![A-Za-z0-9])")
QUESTION_HEADING = "## 待決問題"
QUESTION_LINE = re.compile(r"\| Q\d")
# 和 system-analysis 的 check_plan.py 同一個樣式:「提出的步驟」只能是一個 S<步驟>、tasks 或一個 implement T<編號>
QUESTION_ROW = re.compile(r"^\| Q(\d+) \| (?:S(\d+)|tasks|implement T\d+) \|(.*)\|((?:\\.|[^|\\])*)\|((?:\\.|[^|\\])*)\|$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tasks", required=True, type=Path, help="tasks.md 的路徑")
    parser.add_argument("--phase", required=True, type=int, help="要檢查的 phase 序號,也就是 `## Phase N:` 的 N")
    parser.add_argument("--plan", type=Path, help="plan.md 的路徑;給了才檢查待決問題表每一列的格式")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not args.tasks.is_file():
        print(f"錯誤: 找不到 {args.tasks}。--tasks 要給 tasks.md 的路徑。", file=sys.stderr)
        return 2
    try:
        lines = args.tasks.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        print(f"錯誤: {args.tasks} 不是 UTF-8 編碼。請把它轉存成 UTF-8 再執行。", file=sys.stderr)
        return 2

    checked: dict[str, bool] = {}
    paused: set[str] = set()
    task_phase: dict[str, int | None] = {}
    phase_tasks: list[str] = []
    rows: list[dict] = []
    phases: list[int] = []
    title = None
    current: int | None = None
    in_table = False
    for line in lines:
        heading = PHASE.match(line)
        if heading:
            current = int(heading.group(1))
            phases.append(current)
            if current == args.phase:
                title = heading.group(2)
            in_table = False
            continue
        if line.startswith("## "):
            current, in_table = None, False
            continue
        task = TASK.match(line)
        if task:
            task_id = f"T{task.group(2)}"
            checked[task_id] = task.group(1) in "xX"
            if not checked[task_id] and task.group(4).startswith(PAUSED):
                paused.add(task_id)
            task_phase[task_id] = current
            if current == args.phase:
                phase_tasks.append(task_id)
            continue
        if COVERAGE_HEADING.match(line):
            in_table = current == args.phase
            continue
        if line.startswith("#"):
            in_table = False
            continue
        row = COVERAGE_ROW.match(line) if in_table else None
        if row:
            rows.append({
                "element": row.group(1),
                "implement": ["T" + i for i in TASK_ID.findall(row.group(2))],
                "test": ["T" + i for i in TASK_ID.findall(row.group(3))],
            })

    if title is None:
        known = "、".join(str(n) for n in phases) or "沒有"
        print(f"錯誤: tasks.md 裡沒有 Phase {args.phase}。這份 tasks.md 的 phase 序號有:{known}。", file=sys.stderr)
        return 2

    unchecked_tasks = [t for t in phase_tasks if not checked[t] and t not in paused]
    paused_tasks = [t for t in phase_tasks if t in paused]
    open_rows, deferred_rows, paused_rows = [], [], []
    for row in rows:
        listed = row["implement"] + row["test"]
        unknown = [t for t in listed if t not in checked]
        on_hold = [t for t in listed if t in paused]
        later = [t for t in listed if t in checked and not checked[t] and t not in paused and (task_phase[t] or 0) > args.phase]
        missing = [t for t in listed if t in checked and not checked[t] and t not in paused and t not in later]
        if missing or unknown or not row["implement"] or not row["test"]:
            open_rows.append({**row, "unchecked": missing, "unknown": unknown, "paused": on_hold})
        elif later:
            deferred_rows.append({**row, "later": later, "paused": on_hold})
        elif on_hold:
            paused_rows.append({**row, "paused": on_hold})

    bad_question_rows: list[dict] = []
    if args.plan is not None:
        if not args.plan.is_file():
            print(f"錯誤: 找不到 {args.plan}。--plan 要給 plan.md 的路徑。", file=sys.stderr)
            return 2
        try:
            plan_lines = args.plan.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            print(f"錯誤: {args.plan} 不是 UTF-8 編碼。請把它轉存成 UTF-8 再執行。", file=sys.stderr)
            return 2
        in_questions = False
        for number, line in enumerate(plan_lines, 1):
            if line.startswith("#") and not line.startswith("###"):  # 到下一個同級或更高的標題為止
                in_questions = line.strip() == QUESTION_HEADING
                continue
            row = line.strip()
            if in_questions and QUESTION_LINE.match(row) and not QUESTION_ROW.match(row):
                bad_question_rows.append({"line": number, "row": row[:120]})

    passed = not unchecked_tasks and not open_rows and not bad_question_rows
    result = {
        "tasks": str(args.tasks),
        "phase": args.phase,
        "title": title,
        "passed": passed,
        "task_count": len(phase_tasks),
        "unchecked_tasks": unchecked_tasks,
        "paused_tasks": paused_tasks,
        "coverage_rows": len(rows),
        "open_rows": open_rows,
        "deferred_rows": deferred_rows,
        "paused_rows": paused_rows,
        "bad_question_rows": bad_question_rows,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(
        f"Phase {args.phase}:{len(phase_tasks)} 個任務 {len(unchecked_tasks)} 個沒勾、{len(paused_tasks)} 個 ⏸ 延後;"
        f"介面覆蓋 {len(rows)} 列 {len(open_rows)} 列還有沒勾的任務、{len(deferred_rows)} 列等後面的 phase、{len(paused_rows)} 列只缺 ⏸ 延後任務"
        + (f";待決問題表 {len(bad_question_rows)} 列格式不符" if args.plan is not None else ""),
        file=sys.stderr,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
