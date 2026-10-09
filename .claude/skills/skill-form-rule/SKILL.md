---
name: skill-form-rule
description: 當要撰寫 Skill 時 只要涉及到規則部分 規則的撰寫 `rules/` 底下 Rule File 的撰寫 就必須使用此 Skill。使用者因既有 Skill 的產出不符預期而要求修改時,先用 skill-engineering 分析根因,即使已指定步驟或修法亦同;依已確認方案轉交本 Skill 執行時,直接承接。(未驗證)
---

# SOP

## Phase 1: 寫出 Rule File
1. Read 目標 skill 的 SKILL.md 與已有的 Rule File。
2. Write 依 `rules/RuleFile-格式規範.md` 把使用者要的規則寫成目標 skill `rules/` 底下的 Rule File。
3. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_rule_file.py --file <Rule File 的路徑>` 取得結構檢查的結果;若有不過 → 跳至 Phase 1 Step 2。
4. Think 逐條對照;若有不過 → 跳至 Phase 1 Step 2。
