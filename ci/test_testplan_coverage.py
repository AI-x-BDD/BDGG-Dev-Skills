"""check_testplan.py 的需求覆蓋:範疇內的需求要有存在的案例,或明確不在範疇並寫理由;待測端點表的替身要指到 📏 實跑案例,或寫明無法實跑。

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
EDGE_SPEC = SPEC + "\n### 邊界情況\n\n- 空輸入\n"
HEAD = "# Testplan\n\n- **範疇**:使用者故事 1\n\n### 受測操作\n\n| 寫法 | 說明 |\n|---|---|\n| `GET /x` | 取得 |\n\n"
CASES = (
    "| ID | 受測操作 | 則 | 要抓的錯 |\n|---|---|---|---|\n"
    "| US1-BE-01 | `GET /x` | 則1:回 200 | 回 500 |\n\n"
)
COVERAGE = "## 4. 需求覆蓋\n\n| 需求 | 歸屬 | E2 後端 | 驗證方式 |\n|---|---|---|---|\n{row}\n\n"
EXCLUDED = "## 5. 不在本次範疇\n\n| 需求 | 為什麼不測 | 之後怎麼驗 |\n|---|---|---|\n{rows}\n"


class TestplanCoverageTest(unittest.TestCase):
    def check(self, plan: str, spec: str = SPEC) -> tuple[int, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            spec_path, plan_path = Path(tmp) / "spec.md", Path(tmp) / "testplan.md"
            spec_path.write_text(spec, encoding="utf-8")
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

    def edge_plan(self, edge_row: str, rows: str) -> str:
        row = "| FR-001 範例 | 故事 1 | US1-BE-01 | 🔴🟢 |\n" + edge_row
        return HEAD + CASES + COVERAGE.format(row=row) + EXCLUDED.format(rows=rows)

    def test_edge_excluded_without_reason_fails(self):
        code, result = self.check(self.edge_plan("| 邊界:空輸入 | 故事 1 | 不在範疇 | — |", ""), EDGE_SPEC)
        self.assertEqual(code, 1)
        self.assertTrue(any(v["item"] == "邊界:空輸入" for c in result["checks"] for v in c["violations"]))

    def test_edge_excluded_with_blank_follow_up_fails(self):
        code, _ = self.check(self.edge_plan("| 邊界:空輸入 | 故事 1 | 不在範疇 | — |", "| 邊界:空輸入 | 前端已擋 | |"), EDGE_SPEC)
        self.assertEqual(code, 1)

    def test_edge_excluded_with_reason_passes(self):
        rows = "| 邊界:空輸入 | 前端已擋 | 手動驗收 |"
        code, result = self.check(self.edge_plan("| 邊界:空輸入 | 故事 1 | 不在範疇 | — |", rows), EDGE_SPEC)
        self.assertEqual(code, 0, result)

    def double_plan(self, double: str) -> str:
        endpoints = (
            "## 1. 待測端點\n\n| 端點 | 介面規格檔 | 公開接縫 | 測試等級 | 工具 | 測試環境 | 替身 |\n|---|---|---|---|---|---|---|\n"
            f"| E2 後端 | `api.yaml` | `GET /x` | 整合 | pytest | 暫存庫 | {double} |\n\n"
        )
        measured = (
            "| ID | 品質屬性 | 驗證方式 | 受測操作 | 則 | 要抓的錯 | 副作用與護欄 | 判定者與樣本 |\n|---|---|---|---|---|---|---|---|\n"
            "| US1-BE-02 | 實跑 | 📏 量測 | `GET /x` | 則1:回 200 | 回 500 | 只寫暫存庫 | 判定者:腳本;樣本:不適用 |\n"
            "| US1-BE-03 | 隔離 | 🔴🟢 行為測試 | `GET /x` | 則1:回 200 | 回 500 | — | — |\n\n"
        )
        row = "| FR-001 範例 | 故事 1 | US1-BE-01~US1-BE-03 | 🔴🟢、📏 量測 |"
        return HEAD + endpoints + CASES + measured + COVERAGE.format(row=row) + EXCLUDED.format(rows="")

    def double_violations(self, result: dict) -> list:
        return [v for c in result["checks"] if c["rule"].startswith("每個替身") for v in c["violations"]]

    def test_double_pointing_to_measured_case_passes(self):
        code, result = self.check(self.double_plan("`FakeX`(X 服務)→ US1-BE-02"))
        self.assertEqual(code, 0, result)

    def test_double_pointing_to_undefined_case_fails(self):
        code, result = self.check(self.double_plan("`FakeX`(X 服務)→ US1-BE-09"))
        self.assertEqual(code, 1)
        self.assertTrue(self.double_violations(result), result)

    def test_double_cannot_run_with_reason_passes(self):
        code, result = self.check(self.double_plan("`FakeX`(X 服務)→ 無法實跑:X 服務停機維護"))
        self.assertEqual(code, 0, result)

    def test_double_cannot_run_without_reason_fails(self):
        code, result = self.check(self.double_plan("`FakeX`(X 服務)→ 無法實跑:"))
        self.assertEqual(code, 1)
        self.assertTrue(self.double_violations(result), result)

    def test_double_pointing_to_behaviour_case_fails(self):
        for target in ("US1-BE-03", "US1-BE-01"):
            code, result = self.check(self.double_plan(f"`FakeX`(X 服務)→ {target}"))
            self.assertEqual(code, 1, target)
            self.assertTrue(self.double_violations(result), result)

    def test_second_double_without_case_fails(self):
        code, result = self.check(self.double_plan("`FakeX`(X 服務)→ US1-BE-02<br>`FakeY`(Y 工具)→ US1-BE-03"))
        self.assertEqual(code, 1)
        self.assertEqual([v["item"] for v in self.double_violations(result)], ["E2 後端:`FakeY`(Y 工具)→ US1-BE-03"])

    def test_no_double_is_not_checked(self):
        for cell in ("無", "—"):
            code, result = self.check(self.double_plan(cell))
            self.assertEqual(code, 0, result)


if __name__ == "__main__":
    unittest.main()
