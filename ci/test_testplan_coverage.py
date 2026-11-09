"""check_testplan.py 的需求覆蓋:範疇內的需求要有存在的案例,或明確不在範疇並寫理由。

SKILLS_ROOT 沒設定時檢查 .agents/skills 底下的腳本。
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(os.environ.get("SKILLS_ROOT", Path(__file__).resolve().parent.parent / ".agents" / "skills"))
CHECK_TESTPLAN = ROOT / "testplan" / "scripts" / "check_testplan.py"

SPEC = "# 規格\n\n### 使用者故事 1\n\n- **FR-001** 範例需求\n"
HEAD = "# Testplan\n\n- **範疇**:使用者故事 1\n\n### 受測操作\n\n| 寫法 | 說明 |\n|---|---|\n| `GET /x` | 取得 |\n\n"
CASES = (
    "| ID | 受測操作 | 則 | 要抓的錯 |\n|---|---|---|---|\n"
    "| US1-BE-01 | `GET /x` | 則1:回 200 | 回 500 |\n\n"
)
COVERAGE = "## 4. 需求覆蓋\n\n| 需求 | 歸屬 | E2 後端 | 驗證方式 |\n|---|---|---|---|\n{row}\n\n"
EXCLUDED = "## 5. 不在本次範疇\n\n| 需求 | 為什麼不測 | 之後怎麼驗 |\n|---|---|---|\n{rows}\n"


class TestplanCoverageTest(unittest.TestCase):
    def check(self, plan: str) -> tuple[int, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            spec_path, plan_path = Path(tmp) / "spec.md", Path(tmp) / "testplan.md"
            spec_path.write_text(SPEC, encoding="utf-8")
            plan_path.write_text(plan, encoding="utf-8")
            done = subprocess.run(
                [sys.executable, str(CHECK_TESTPLAN), "--spec", str(spec_path), "--plan", str(plan_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        body = done.stdout.split("\n", 1)[1] if done.stdout else "{}"
        return done.returncode, json.loads(body)

    def test_row_with_case_passes(self):
        plan = HEAD + CASES + COVERAGE.format(row="| FR-001 範例 | 故事 1 | US1-BE-01 | 🔴🟢 |") + EXCLUDED.format(rows="")
        code, result = self.check(plan)
        self.assertEqual(code, 0, result)

    def test_row_of_dashes_fails(self):
        plan = HEAD + COVERAGE.format(row="| FR-001 範例 | 故事 1 | — | — |") + EXCLUDED.format(rows="")
        code, result = self.check(plan)
        self.assertEqual(code, 1)
        self.assertTrue(any(v["item"] == "FR-001" for c in result["checks"] for v in c["violations"]))

    def test_row_pointing_to_undefined_case_fails(self):
        plan = HEAD + COVERAGE.format(row="| FR-001 範例 | 故事 1 | US1-BE-09 | 🔴🟢 |") + EXCLUDED.format(rows="")
        code, _ = self.check(plan)
        self.assertEqual(code, 1)

    def test_excluded_without_reason_fails(self):
        plan = HEAD + COVERAGE.format(row="| FR-001 範例 | 故事 1 | 不在範疇 | — |") + EXCLUDED.format(rows="")
        code, _ = self.check(plan)
        self.assertEqual(code, 1)

    def test_excluded_with_reason_passes(self):
        rows = "| FR-001 範例 | 負向事實,測不出 | code review 確認 |"
        plan = HEAD + COVERAGE.format(row="| FR-001 範例 | 故事 1 | 不在範疇 | — |") + EXCLUDED.format(rows=rows)
        code, result = self.check(plan)
        self.assertEqual(code, 0, result)


if __name__ == "__main__":
    unittest.main()
