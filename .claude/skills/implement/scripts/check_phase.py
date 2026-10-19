# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查 tasks.md 裡一個 phase 的勾選狀態。

任務        這個 phase 的每個任務是否都勾成 [X]
介面覆蓋    這個 phase 的介面覆蓋表,每一列的實作欄與測試欄寫的任務是否都勾了;
            寫的是後面 phase 的任務時,那一列列在 deferred_rows(還沒輪到),不算不過
結果以 JSON 寫到 stdout;這個 phase 或前面 phase 有沒勾的任務、覆蓋列時 exit code 是 1,參數或檔案有誤時是 2。
"""

import argparse
import json
import re
import sys
from pathlib import Path

PHASE = re.compile(r"^## Phase (\d+):\s*(.+?)\s*$")
TASK = re.compile(r"^- \[([ xX])\] T(\d{3})\b")
COVERAGE_HEADING = re.compile(r"^### 介面覆蓋[((](.+?)[))]")
COVERAGE_ROW = re.compile(r"^\| (`.+?) \| (.*?) \| (.*?) \|$")
TASK_ID = re.compile(r"T(\d{3})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tasks", required=True, type=Path, help="tasks.md 的路徑")
    parser.add_argument("--phase", required=True, type=int, help="要檢查的 phase 序號,也就是 `## Phase N:` 的 N")
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

    unchecked_tasks = [t for t in phase_tasks if not checked[t]]
    open_rows, deferred_rows = [], []
    for row in rows:
        listed = row["implement"] + row["test"]
        unknown = [t for t in listed if t not in checked]
        later = [t for t in listed if t in checked and not checked[t] and (task_phase[t] or 0) > args.phase]
        missing = [t for t in listed if t in checked and not checked[t] and t not in later]
        if missing or unknown or not row["implement"] or not row["test"]:
            open_rows.append({**row, "unchecked": missing, "unknown": unknown})
        elif later:
            deferred_rows.append({**row, "later": later})

    passed = not unchecked_tasks and not open_rows
    result = {
        "tasks": str(args.tasks),
        "phase": args.phase,
        "title": title,
        "passed": passed,
        "task_count": len(phase_tasks),
        "unchecked_tasks": unchecked_tasks,
        "coverage_rows": len(rows),
        "open_rows": open_rows,
        "deferred_rows": deferred_rows,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(
        f"Phase {args.phase}:{len(phase_tasks)} 個任務 {len(unchecked_tasks)} 個沒勾;介面覆蓋 {len(rows)} 列 {len(open_rows)} 列還有沒勾的任務、{len(deferred_rows)} 列等後面的 phase",
        file=sys.stderr,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
