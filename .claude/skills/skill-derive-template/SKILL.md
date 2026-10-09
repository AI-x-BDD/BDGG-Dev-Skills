---
name: skill-derive-template
description: 給定一支已經寫好的 SOP skill,使用者想針對其中某個步驟,把該步驟生成內容的格式抽成樣板時,就必須使用此 Skill(未驗證)
---

# SOP

## Phase 1: 提出抽出後的樣子
1. Read 目標 skill 的 SKILL.md 與已有的樣板;若使用者已講明要抽哪一步、那一步生成的內容要長什麼樣子 → 跳至 Phase 1 Step 3。
2. Ask 依 `rules/提問-規範.md` 問使用者要抽哪一步(Phase N Step M)、那一步生成的內容要長什麼樣子。
3. Think 依 `rules/抽出-規範.md` 決定抽出後的樣子:樣板名字與格式、骨架有哪些填位符號、指定那一步改成什麼寫法。
4. Ask 提出抽出後的樣子,問使用者是否可以寫入;若使用者要修改 → 跳至 Phase 1 Step 3。

## Phase 2: 寫出樣板
1. Delegate 轉交 skill-form-template,把那一步生成內容的格式寫成骨架與範例。

## Phase 3: 改寫指定步驟
1. Delegate 轉交 skill-form-sop,把指定那一步改成抽出後的寫法。
