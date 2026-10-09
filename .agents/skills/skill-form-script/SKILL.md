---
name: skill-form-script
description: 當要撰寫 Skill 時,只要涉及腳本的部分(`scripts/` 底下 Python 腳本的撰寫),就必須使用此 Skill。使用者因既有 Skill 的產出不符預期而要求修改時,先用 skill-engineering 分析根因,即使已指定步驟或修法亦同;依已確認方案轉交本 Skill 執行時,直接承接。(未驗證)
---

# SOP

## Phase 1: 補上腳本執行規範
1. Read 目標 skill 的 SKILL.md、`rules/` 與 `scripts/` 底下已有的檔;若目標 skill 已有 `rules/腳本執行-規範.md` → 跳至 Phase 2 Step 1。
2. Write 依 `rules/腳本執行規範-格式規範.md` 在目標 skill 的 `rules/` 補上 `腳本執行-規範.md`。

## Phase 2: 寫出腳本
1. Write 依 `rules/腳本-格式規範.md` 把使用者要的處理寫成目標 skill `scripts/` 底下的 Python 腳本。
2. Read 這支腳本以 `uv run` 執行 `--help` 與一筆實際輸入的輸出;若與使用者要的結果不符 → 跳至 Phase 2 Step 1。
3. Think 逐條對照;若有不過 → 跳至 Phase 2 Step 1。
