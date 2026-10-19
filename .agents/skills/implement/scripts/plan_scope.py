# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""列出一份 tasks.md 在指定範圍內的任務與還沒決定的待決問題。

範圍對齊:範圍碰到的 phase 一律整個納入,終點延到那個 phase 的 Checkpoint;因此多出來的任務列在 extended
前置未完成:範圍第一個 phase 之前還沒勾選的任務列在 pending_before
同檔任務:這次要做的任務(範圍內與 pending_before)有兩個以上還沒勾選、描述裡寫了同一個檔案路徑的,列在 shared_files
待決問題:範圍內任務的 📎 引用 plan.md § Q,而 plan.md 待決問題表的「決定」欄是 — 或空白的,列在 open_questions
結果以 JSON 寫到 stdout;範圍寫錯或檔案讀不到時 exit code 是 2。
"""

import argparse
import json
import re
import sys
from pathlib import Path

PHASE = re.compile(r"^## Phase (\d+):\s*(.+?)\s*$")
STORY = re.compile(r"User Story (\d+)")
SECTION = re.compile(r"^### (.+?)\s*$")
SUBSECTION = re.compile(r"^#### (.+?)\s*$")
TASK = re.compile(r"^- \[([ xX])\] T(\d{3})\b\s*(\[P\]\s*)?(\[US(\d+)\]\s*)?(.*)$")
CLIP = re.compile(r"^\s+- 📎 (.*)$")
CHECKPOINT = re.compile(r"^\*\*Checkpoint\*\*:\s*(.*)$")
CODE = re.compile(r"`([^`]+)`")
PATH_LIKE = re.compile(r"^[\w.@{}*,\-]+(/[\w.@{}*,\-]+)*/?$")
FILE_SUFFIX = re.compile(
    r"\.(ts|tsx|js|jsx|mjs|cjs|json|jsonc|ya?ml|toml|md|html?|css|scss|conf|ini|env|sh|py|sql|dbml|lock|txt|svg|png|ico|xml)$"
)
FILE_NAME = re.compile(r"(^|/)(Dockerfile[\w.-]*|Makefile|\.gitignore|\.dockerignore|\.env[\w.-]*|\.\w+rc(\.\w+)?)$")
PLAN_REF = re.compile(r"`(?:[^`]*/)?plan\.md`\s*§\s*([^;;]*)")
Q_RANGE = re.compile(r"Q(\d+)\s*[–-]\s*Q?(\d+)")
Q_ONE = re.compile(r"Q(\d+)")
OPEN_HEADING = re.compile(r"^## 待決問題\s*$")
QUESTION_ROW = re.compile(r"^\|\s*Q(\d+)\s*\|(.*)\|\s*$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")  # Markdown 表格裡跳脫的 \| 是內容,不是欄分隔
UNDECIDED = {"", "—", "-", "–"}


def read_text(path: Path, what: str) -> str:
    if not path.is_file():
        print(f"錯誤: 找不到 {path}。{what}", file=sys.stderr)
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"錯誤: {path} 不是 UTF-8 編碼。請把它轉存成 UTF-8 再執行。", file=sys.stderr)
        sys.exit(2)


def phase_kind(title: str) -> str:
    lowered = title.lower()
    if lowered.startswith("setup"):
        return "setup"
    if lowered.startswith("foundational"):
        return "foundational"
    if STORY.search(title):
        return "story"
    if lowered.startswith("polish"):
        return "polish"
    return "other"


def file_paths(description: str) -> list[str]:
    """取出描述裡反引號包起來、長得像檔案路徑的字串(有 /、常見副檔名或 Dockerfile 這類固定檔名,沒有空白;`@scope/name` 是套件名稱,`match.start` 這類訊息名稱不算)。"""
    found: list[str] = []
    for token in CODE.findall(description):
        token = token.strip()
        if token.startswith("@") or not PATH_LIKE.match(token):
            continue
        if "/" in token or FILE_SUFFIX.search(token) or FILE_NAME.search(token):
            if token not in found:
                found.append(token)
    return found


def question_ids(clip: str) -> set[int]:
    ids: set[int] = set()
    for match in PLAN_REF.finditer(clip):
        text = match.group(1)
        for start, end in Q_RANGE.findall(text):
            ids.update(range(int(start), int(end) + 1))
        ids.update(int(q) for q in Q_ONE.findall(Q_RANGE.sub("", text)))
    return ids


def parse_tasks(text: str) -> list[dict]:
    phases: list[dict] = []
    current_task: dict | None = None
    section = subsection = None
    for line in text.splitlines():
        heading = PHASE.match(line)
        if heading:
            title = heading.group(2)
            story = STORY.search(title)
            phases.append({
                "number": int(heading.group(1)),
                "title": title,
                "kind": phase_kind(title),
                "story": f"US{story.group(1)}" if story else None,
                "checkpoint": None,
                "tasks": [],
            })
            section = subsection = current_task = None
            continue
        if line.startswith("## "):
            phases.append({"number": None, "title": line[3:].strip(), "kind": "outside", "story": None, "checkpoint": None, "tasks": []})
            section = subsection = current_task = None
            continue
        if not phases:
            continue
        phase = phases[-1]
        if SECTION.match(line):
            section, subsection, current_task = SECTION.match(line).group(1), None, None
            continue
        if SUBSECTION.match(line):
            subsection, current_task = SUBSECTION.match(line).group(1), None
            continue
        checkpoint = CHECKPOINT.match(line)
        if checkpoint:
            phase["checkpoint"] = checkpoint.group(1)
            current_task = None
            continue
        task = TASK.match(line)
        if task:
            mark, number, parallel, _, story, description = task.groups()
            current_task = {
                "id": f"T{number}",
                "parallel": bool(parallel),
                "story": f"US{story}" if story else None,
                "section": section,
                "subsection": subsection,
                "checked": mark in "xX",
                "files": file_paths(description),
                "questions": [],
            }
            phase["tasks"].append(current_task)
            continue
        clip = CLIP.match(line)
        if clip and current_task:
            current_task["questions"] = sorted(set(current_task["questions"]) | question_ids(clip.group(1)))
    return [p for p in phases if p["kind"] != "outside"]


def parse_questions(text: str) -> dict[int, dict]:
    questions: dict[int, dict] = {}
    inside = False
    for line in text.splitlines():
        if OPEN_HEADING.match(line):
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        row = QUESTION_ROW.match(line) if inside else None
        if not row:
            continue
        cells = [cell.strip() for cell in CELL_SPLIT.split(row.group(2))]
        if len(cells) < 4:
            continue
        step, question, blocks, decision = cells[0], cells[1], cells[2], cells[-1]
        if int(row.group(1)) in questions:
            print(f"提醒: plan.md 的待決問題表有兩列都是 Q{row.group(1)},以後面那一列為準。", file=sys.stderr)
        questions[int(row.group(1))] = {"step": step, "question": question, "blocks": blocks, "decided": decision not in UNDECIDED}
    return questions


def select_phases(phases: list[dict], scope: str | None) -> list[int]:
    """回傳範圍碰到的 phase 在 phases 裡的索引;範圍寫錯時結束並說明可以用的寫法。"""
    if not scope:
        return list(range(len(phases)))
    chosen: set[int] = set()
    for raw in scope.split(","):
        token = raw.strip()
        compact = token.replace(" ", "").lower()
        hit: list[int] = []
        if re.fullmatch(r"phase\d+", compact):
            hit = [i for i, p in enumerate(phases) if p["number"] == int(compact[5:])]
        elif re.fullmatch(r"us\d+", compact):
            hit = [i for i, p in enumerate(phases) if p["story"] == f"US{int(compact[2:])}"]
        elif compact in ("setup", "foundational", "polish"):
            hit = [i for i, p in enumerate(phases) if p["kind"] == compact]
        elif re.fullmatch(r"t\d{1,3}", compact):
            wanted = f"T{int(compact[1:]):03d}"
            hit = [i for i, p in enumerate(phases) if any(t["id"] == wanted for t in p["tasks"])]
        else:
            print(f"錯誤: --scope 裡的「{token}」看不懂。可以寫 `Phase 2`、`US1`、`T030`、`Setup`、`Foundational`、`Polish`,多個用逗號分開;省略代表全部。", file=sys.stderr)
            sys.exit(2)
        if not hit:
            known = ", ".join(f"Phase {p['number']}" + (f"({p['story']})" if p["story"] else "") for p in phases)
            print(f"錯誤: --scope 的「{token}」在 tasks.md 裡找不到。這份 tasks.md 有:{known};任務編號從 T001 到 T{len([t for p in phases for t in p['tasks']]):03d}。", file=sys.stderr)
            sys.exit(2)
        chosen.update(hit)
    return sorted(chosen)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tasks", required=True, type=Path, help="tasks.md 的路徑")
    parser.add_argument("--plan", required=True, type=Path, help="plan.md 的路徑(讀它的「## 待決問題」表)")
    parser.add_argument("--scope", help="這次要做的範圍:`Phase 2`、`US1`、`T030`、`Setup`、`Foundational`、`Polish`,多個用逗號分開;省略代表 tasks.md 的全部 phase")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    phases = parse_tasks(read_text(args.tasks, "--tasks 要給 tasks.md 的路徑。"))
    if not phases:
        print(f"錯誤: {args.tasks} 裡沒有任何 `## Phase N:` 標題。--tasks 要給 tasks skill 產出的 tasks.md。", file=sys.stderr)
        return 2
    questions = parse_questions(read_text(args.plan, "--plan 要給 plan.md 的路徑。"))
    if not questions:
        print(f"提醒: {args.plan} 沒有「## 待決問題」表或表是空的,open_questions 會是空的。", file=sys.stderr)

    chosen = select_phases(phases, args.scope)
    explicit: set[str] = set()
    if args.scope:
        for raw in args.scope.split(","):
            compact = raw.strip().replace(" ", "").lower()
            if re.fullmatch(r"t\d{1,3}", compact):
                # 指定到任務時,同一個 phase 裡排在它前面的任務也算明講的範圍
                wanted = int(compact[1:])
                explicit.update(t["id"] for i in chosen for t in phases[i]["tasks"] if int(t["id"][1:]) <= wanted)
            else:
                for i in select_phases(phases, raw):
                    explicit.update(t["id"] for t in phases[i]["tasks"])
    in_scope = [phases[i] for i in chosen]
    scope_ids = [t["id"] for p in in_scope for t in p["tasks"]]
    extended = [i for i in scope_ids if args.scope and i not in explicit]
    pending_before = [t["id"] for p in phases[: chosen[0]] for t in p["tasks"] if not t["checked"]]

    by_file: dict[str, list[str]] = {}
    for phase in phases[: chosen[0]] + in_scope:
        for task in phase["tasks"]:
            if not task["checked"]:
                for path in task["files"]:
                    by_file.setdefault(path, []).append(task["id"])
    shared_files = [{"file": path, "tasks": ids} for path, ids in by_file.items() if len(ids) > 1]

    referenced: dict[int, list[str]] = {}
    for phase in in_scope:
        for task in phase["tasks"]:
            for q in task["questions"]:
                referenced.setdefault(q, []).append(task["id"])
    open_questions = [
        {"id": f"Q{q}", "step": questions[q]["step"], "question": questions[q]["question"], "blocks": questions[q]["blocks"], "tasks": ids}
        for q, ids in sorted(referenced.items())
        if q in questions and not questions[q]["decided"]
    ]
    missing = [f"Q{q}" for q in sorted(referenced) if q not in questions]
    if missing:
        print(f"提醒: 範圍內的任務引用了 {'、'.join(missing)},但 plan.md 的待決問題表裡沒有這幾題。", file=sys.stderr)

    result = {
        "tasks": str(args.tasks),
        "plan": str(args.plan),
        "scope": args.scope or "全部",
        "phases": [{key: p[key] for key in ("number", "title", "kind", "story", "checkpoint", "tasks")} for p in in_scope],
        "end_checkpoint": {"phase": in_scope[-1]["number"], "text": in_scope[-1]["checkpoint"]},
        "extended": extended,
        "pending_before": pending_before,
        "shared_files": shared_files,
        "open_questions": open_questions,
        "summary": {
            "tasks": len(scope_ids),
            "unchecked": sum(1 for p in in_scope for t in p["tasks"] if not t["checked"]),
            "extended": len(extended),
            "pending_before": len(pending_before),
            "open_questions": len(open_questions),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    s = result["summary"]
    print(f"範圍內 {s['tasks']} 個任務({s['unchecked']} 個未勾),對齊延入 {s['extended']} 個,前置未完成 {s['pending_before']} 個,待決問題 {s['open_questions']} 題", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
