"""tasks.md 任務編號帶小寫字尾(T001a、T001b,homelab-rebuild R66)時,implement 與 tasks 的腳本要認得。

apps/service-template 的 spec-tasks CI 已接受 `T[0-9]{3}[[:lower:]]?`;這裡確認 check_phase.py、check_tasks.py、
plan_scope.py 和它一致。用法:python3 ci/test_task_ids.py(要裝 pyyaml);
SKILLS_ROOT 環境變數可以指到別的 .agents/skills 目錄,拿修改前的腳本當對照組。
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(os.environ.get("SKILLS_ROOT", Path(__file__).resolve().parent.parent / ".agents" / "skills"))
CHECK_PHASE = ROOT / "implement" / "scripts" / "check_phase.py"
CHECK_TASKS = ROOT / "tasks" / "scripts" / "check_tasks.py"
PLAN_SCOPE = ROOT / "implement" / "scripts" / "plan_scope.py"

SPEC = "# 規格\n\n- **FR-001** 範例需求\n"
PLAN = "# Plan\n\n## 待決問題\n\n| 編號 | 步驟 | 問題 | 卡住 | 決定 |\n|---|---|---|---|---|\n"


def tasks_md(lines: list[str], coverage: str = "") -> str:
    body = "".join(f"- [{mark}] {task_id} 建立 `{task_id.lower()}/README.md`\n  - 📎 `spec.md` § FR-001\n" for mark, task_id in lines)
    return f"# Tasks\n\n## Phase 1: Setup\n\n{body}{coverage}\n**Checkpoint**: 完成\n\n## Phase 2: Polish\n\n- [ ] T009 收尾 `z/README.md`\n  - 📎 `spec.md` § FR-001\n"


def run(script: Path, *args: str) -> tuple[int, dict]:
    done = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, encoding="utf-8")
    try:
        return done.returncode, json.loads(done.stdout)
    except json.JSONDecodeError:
        return done.returncode, {"stdout": done.stdout, "stderr": done.stderr}


class TaskIdTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.package = Path(self.dir.name)
        (self.package / "spec.md").write_text(SPEC, encoding="utf-8")
        (self.package / "plan.md").write_text(PLAN, encoding="utf-8")
        self.tasks = self.package / "tasks.md"

    def tearDown(self) -> None:
        self.dir.cleanup()

    def write(self, lines: list[tuple[str, str]], coverage: str = "", tail: str = "T009") -> None:
        text = tasks_md(lines, coverage).replace("T009", tail)
        self.tasks.write_text(text, encoding="utf-8")

    def ids_check(self) -> dict:
        _, result = run(CHECK_TASKS, "--tasks", str(self.tasks), "--package", str(self.package))
        return next(c for c in result.get("checks", []) if c["check"].startswith("任務編號"))

    # check_phase.py
    def test_phase_sees_unchecked_subtask(self) -> None:
        self.write([("X", "T001a"), (" ", "T001b"), ("X", "T002")], tail="T003")
        code, result = run(CHECK_PHASE, "--tasks", str(self.tasks), "--phase", "1")
        self.assertEqual(code, 1)
        self.assertEqual(result.get("unchecked_tasks"), ["T001b"])
        self.assertEqual(result.get("task_count"), 3)

    def test_phase_passes_when_subtasks_ticked(self) -> None:
        self.write([("X", "T001a"), ("X", "T001b"), ("X", "T002")], tail="T003")
        code, result = run(CHECK_PHASE, "--tasks", str(self.tasks), "--phase", "1")
        self.assertEqual(code, 0, result)
        self.assertEqual(result.get("task_count"), 3)

    def test_phase_coverage_cell_keeps_suffix(self) -> None:
        coverage = "\n### 介面覆蓋(Setup)\n\n| 元素 | 實作 | 測試 |\n|---|---|---|\n| `x` § y | T001a | T001b |\n"
        self.write([("X", "T001a"), (" ", "T001b"), ("X", "T002")], coverage, tail="T003")
        _, result = run(CHECK_PHASE, "--tasks", str(self.tasks), "--phase", "1")
        rows = result.get("open_rows", [])
        self.assertEqual(len(rows), 1, result)
        self.assertEqual(rows[0]["implement"], ["T001a"])
        self.assertEqual(rows[0]["unchecked"], ["T001b"])
        self.assertEqual(rows[0]["unknown"], [])

    # check_tasks.py
    def test_ids_accept_subtasks(self) -> None:
        self.write([(" ", "T001a"), (" ", "T001b"), (" ", "T002"), (" ", "T003a")], tail="T004")
        self.assertEqual(self.ids_check()["result"], "過")

    def test_ids_reject_plain_and_suffixed_same_number(self) -> None:
        self.write([(" ", "T001"), (" ", "T001a"), (" ", "T002")], tail="T003")
        self.assertEqual(self.ids_check()["result"], "不過")

    def test_ids_reject_suffix_gap(self) -> None:
        self.write([(" ", "T001a"), (" ", "T001c"), (" ", "T002")], tail="T003")
        self.assertEqual(self.ids_check()["result"], "不過")

    def test_ids_reject_number_gap(self) -> None:
        self.write([(" ", "T001"), (" ", "T003")], tail="T004")
        self.assertEqual(self.ids_check()["result"], "不過")

    def test_ids_reject_duplicate_subtask(self) -> None:
        self.write([(" ", "T001a"), (" ", "T001a"), (" ", "T002")], tail="T003")
        self.assertEqual(self.ids_check()["result"], "不過")

    # plan_scope.py
    def test_scope_accepts_subtask(self) -> None:
        self.write([(" ", "T001a"), (" ", "T001b"), (" ", "T002")], tail="T003")
        code, result = run(PLAN_SCOPE, "--tasks", str(self.tasks), "--plan", str(self.package / "plan.md"), "--scope", "T001a")
        self.assertEqual(code, 0, result)
        ids = [t["id"] for p in result["phases"] for t in p["tasks"]]
        self.assertEqual(ids, ["T001a", "T001b", "T002"])
        self.assertEqual(result["extended"], ["T001b", "T002"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
