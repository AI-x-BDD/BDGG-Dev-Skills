"""tasks.md 用 ⏸ 標排除或延後的任務(Kevin 2026-10-27)時,implement 的 check_phase.py 要認得。

描述開頭(在 [P]、[US1] 這類標籤之後)是 ⏸ 的未勾任務列在 paused_tasks、不算沒勾;
覆蓋列沒勾的只有 ⏸ 任務時列在 paused_rows、不算不過;一般沒勾的任務照樣不過。
用法:python3 ci/test_paused_tasks.py;SKILLS_ROOT 環境變數可以指到別的 .agents/skills 目錄,拿修改前的腳本當對照組。
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

COVERAGE_HEAD = "\n### 介面覆蓋(US1)\n\n| 元素 | 實作 | 測試 |\n|---|---|---|\n"


def run(tasks: Path, phase: int) -> tuple[int, dict, str]:
    done = subprocess.run([sys.executable, str(CHECK_PHASE), "--tasks", str(tasks), "--phase", str(phase)],
                          capture_output=True, text=True, encoding="utf-8")
    try:
        return done.returncode, json.loads(done.stdout), done.stderr
    except json.JSONDecodeError:
        return done.returncode, {"stdout": done.stdout}, done.stderr


class PausedTaskTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.tasks = Path(self.dir.name) / "tasks.md"

    def tearDown(self) -> None:
        self.dir.cleanup()

    def write(self, phase1: list[str], coverage: list[str] | None = None) -> None:
        table = COVERAGE_HEAD + "".join(f"{r}\n" for r in coverage) if coverage else ""
        text = ("# Tasks\n\n## Phase 1: User Story 1 - 範例\n\n" + "".join(f"{t}\n  - 📎 `spec.md` § FR-001\n" for t in phase1)
                + table + "\n**Checkpoint**: 完成\n\n## Phase 2: Polish\n\n- [ ] T020 收尾 `z/README.md`\n")
        self.tasks.write_text(text, encoding="utf-8")

    def test_paused_task_not_unchecked(self) -> None:
        self.write([
            "- [X] T001 [P] [US1] 實作 `a.py`",
            "- [ ] T002 [P] [US1] ⏸ 撰寫 `tests/test_a.py`(⏸ R51 延後)",
            "- [ ] T003 ⏸ 實作 `b.py`(⏸ R100 排除)",
            "- [ ] T004a [US1] ⏸ 實作 `c.py`(⏸ 延後)",
        ])
        code, result, stderr = run(self.tasks, 1)
        self.assertEqual(code, 0, result)
        self.assertTrue(result.get("passed"))
        self.assertEqual(result.get("unchecked_tasks"), [])
        self.assertEqual(result.get("paused_tasks"), ["T002", "T003", "T004a"])
        self.assertEqual(result.get("task_count"), 4)
        self.assertIn("3 個 ⏸ 延後", stderr)

    def test_row_missing_only_paused_is_not_open(self) -> None:
        self.write(
            ["- [X] T001 [US1] 實作 `a.py`", "- [ ] T002 [P] [US1] ⏸ 撰寫 `tests/test_a.py`(⏸ R51 延後)"],
            ["| `a.yaml` § `paths./a.get` | T001 | T002 |", "| `a.yaml` § `paths./b.get` | T001 | T001 |"],
        )
        code, result, stderr = run(self.tasks, 1)
        self.assertEqual(code, 0, result)
        self.assertEqual(result.get("open_rows"), [])
        rows = result.get("paused_rows", [])
        self.assertEqual(len(rows), 1, result)
        self.assertEqual(rows[0]["element"], "`a.yaml` § `paths./a.get`")
        self.assertEqual(rows[0]["paused"], ["T002"])
        self.assertIn("1 列只缺 ⏸ 延後任務", stderr)

    def test_plain_unchecked_still_fails(self) -> None:
        self.write(
            ["- [ ] T001 [US1] 實作 `a.py`", "- [ ] T002 [P] [US1] ⏸ 撰寫 `tests/test_a.py`(⏸ R51 延後)",
             "- [ ] T003 [US1] 撰寫 `tests/test_b.py`,說明裡提到 ⏸ 但不在開頭"],
            ["| `a.yaml` § `paths./a.get` | T001 | T002 |"],
        )
        code, result, _ = run(self.tasks, 1)
        self.assertEqual(code, 1, result)
        self.assertFalse(result.get("passed"))
        self.assertEqual(result.get("unchecked_tasks"), ["T001", "T003"])
        self.assertEqual(result.get("paused_tasks"), ["T002"])
        rows = result.get("open_rows", [])
        self.assertEqual(len(rows), 1, result)
        self.assertEqual(rows[0]["unchecked"], ["T001"])
        self.assertEqual(rows[0]["paused"], ["T002"])
        self.assertEqual(result.get("paused_rows"), [])

    def test_checked_task_with_pause_mark_counts_as_checked(self) -> None:
        self.write(["- [X] T001 [US1] ⏸ 實作 `a.py`(恢復後已做完)"])
        code, result, _ = run(self.tasks, 1)
        self.assertEqual(code, 0, result)
        self.assertEqual(result.get("paused_tasks"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
