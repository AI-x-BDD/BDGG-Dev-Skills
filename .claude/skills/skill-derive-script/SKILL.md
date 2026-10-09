---
name: skill-derive-script
description: 給定一支已經寫好的 SOP skill,使用者想針對其中某個步驟,把該步驟的職責委派給 Python 腳本執行時,就必須使用此 Skill(未驗證)
---

# SOP

## Phase 1: 提出委派後的樣子
1. Read 目標 skill 的 SKILL.md 與 `scripts/` 底下已有的腳本;若使用者已講明要委派哪一步、腳本吃什麼吐什麼 → 跳至 Phase 1 Step 3。
2. Ask 依 `rules/提問-規範.md` 問使用者要委派哪一步(Phase N Step M)、腳本吃什麼吐什麼。
3. Think 依 `rules/委派-規範.md` 決定委派後的樣子:腳本檔名、參數與輸出、第三方套件、指定那一步改成什麼寫法;若符合〈沿用已確認的具體轉換〉 → 跳至 Phase 2 Step 1。
4. Ask 提出委派後的樣子,問使用者是否可以寫入;若使用者要修改 → 跳至 Phase 1 Step 3。

## Phase 2: 寫出腳本
1. Delegate 轉交 skill-form-script,把那一步的職責寫成腳本。

## Phase 3: 改寫指定步驟
1. Delegate 轉交 skill-form-sop,把指定那一步改成委派後的寫法。
