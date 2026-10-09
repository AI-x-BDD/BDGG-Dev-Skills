---
name: plan-with-class-diagram
description: 寫程式之前,先用 Mermaid 類別圖提案這次開發的類別組織,使用者確認後才按圖依序開發。(未驗證)
---

# SOP

## Phase 1: 提出類別圖
1. Read 這次開發會動到的現有程式碼。
2. Think 依 `rules/類別圖-規範.md` 設計這次開發的類別組織:有哪些類別、各自的職責、彼此的關係。
3. Ask 依 `rules/確認-規範.md` 用 Mermaid `classDiagram` 提出這份設計,問使用者是否可以進入開發;若使用者要修改 → 跳至 Phase 1 Step 2。

## Phase 2: 按圖實作類別
1. Think 依 `rules/實作-規範.md` 依類別之間的相依關係,排出開發順序。
2. Write 依這個順序逐一實作類別圖裡的類別;若必須偏離類別圖 → 跳至 Phase 1 Step 2。
