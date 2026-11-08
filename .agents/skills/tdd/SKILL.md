---
name: tdd
description: 要先寫測試再寫程式、用測試驅動新增功能或修 bug 時,用這支 Skill 先和使用者確認要測的接縫,再一次一個切片走紅燈到綠燈,每個測試只透過公開介面驗證行為;使用者提到 TDD、測試驅動、test-first、先寫測試、紅綠燈、red-green-refactor、整合測試、integration test 時使用。(未驗證)
---

# SOP

## Phase 1: 提出接縫清單
1. Read **這次會動到的程式碼與既有測試**,專案有 `GLOSSARY.md` 與這一區的 ADR 時一併讀。
2. Think 依 `rules/接縫-規範.md` **列出這次要測的接縫**。
3. Ask 依骨架 `templates/接縫清單.md` 與範例 `templates/接縫清單.example.md` **提出接縫清單**,問使用者是否同意只在這些接縫測試;若使用者要修改 → 跳至 Phase 1 Step 2。

## Phase 2: 逐片紅綠實作功能
1. Write 依 `rules/測試-規範.md` 在一個確認過的接縫**寫一個測試**。
2. Read **執行這個測試確認它失敗**;若它沒有失敗 → 跳至 Phase 2 Step 1。
3. Write 依 `rules/實作-規範.md` **只寫剛好讓它通過的程式碼**。
4. Read **執行全部測試確認都通過**;若有測試失敗 → 跳至 Phase 2 Step 3;若還有這次要做的行為沒有測試 → 跳至 Phase 2 Step 1。
5. Report **列出每個切片的紅綠證據**:測試名稱、紅燈時的失敗訊息與綠燈時的測試結果,以及這一輪看到、留給 `code-review` 整理的地方。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出接縫清單"]
        P1S1["1. Read：這次會動到<br/>的程式碼與既有測試"]
        P1S2["2. Think：列出這次要測的接縫"]
        P1S3["3. Ask：提出接縫清單"]
        G_P1S3_1{"使用者要修改？"}
    end
    subgraph P2["Phase 2: 逐片紅綠實作功能"]
        P2S1["1. Write：寫一個測試"]
        P2S2["2. Read：執行這個測試確認它失敗"]
        G_P2S2_1{"它沒有失敗？"}
        P2S3["3. Write：只寫剛好讓它通過的程式碼"]
        P2S4["4. Read：執行全部測試確認都通過"]
        G_P2S4_1{"有測試失敗？"}
        G_P2S4_2{"還有這次要做的<br/>行為沒有測試？"}
        P2S5["5. Report：列出每個切片的紅綠證據"]
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| P1S2
    G_P1S3_1 -->|否| P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P2S1
    G_P2S2_1 -->|否| P2S3
    P2S3 --> P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P2S3
    G_P2S4_1 -->|否| G_P2S4_2
    G_P2S4_2 -->|是| P2S1
    G_P2S4_2 -->|否| P2S5
    P2S5 --> End
```
</details>
