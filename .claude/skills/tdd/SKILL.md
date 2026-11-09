---
name: tdd
description: 要先寫測試再寫程式、用測試驅動新增功能或修 bug 時,用這支 Skill 先和使用者確認要測的接縫,再一次一個切片走紅燈到綠燈、在綠燈下重構,每個測試只透過公開介面驗證行為;呼叫方指定紅燈、綠燈或重構與 testplan.md 的案例時,只做那一步、接縫取自 testplan;使用者提到 TDD、測試驅動、test-first、先寫測試、紅綠燈、red-green-refactor、整合測試、integration test 時使用。(未驗證)
---

# SOP

## Phase 1: 提出接縫清單
1. Read **這次會動到的程式碼與既有測試**,專案有 `GLOSSARY.md` 與這一區的 ADR 時一併讀;若呼叫方指定了紅燈與 `testplan.md` 的案例 → 跳至 Phase 2 Step 1;若呼叫方指定了綠燈與 `testplan.md` 的案例 → 跳至 Phase 2 Step 3;若呼叫方指定了重構 → 跳至 Phase 3 Step 1。
2. Think 依 `rules/接縫-規範.md` **列出這次要測的接縫**。
3. Ask 依骨架 `templates/接縫清單.md` 與範例 `templates/接縫清單.example.md` **提出接縫清單**,問使用者是否同意只在這些接縫測試;若使用者要修改 → 跳至 Phase 1 Step 2。

## Phase 2: 逐片紅綠實作功能
1. Write 依 `rules/測試-規範.md`、骨架 `templates/測試.py` 與範例 `templates/測試.example.py` 在一個確認過的接縫**寫一個測試**。
2. Read 依 `rules/紅燈-規範.md` **執行這個測試確認它是斷言失敗**;若它不是斷言失敗 → 跳至 Phase 2 Step 1;若呼叫方只指定紅燈 → 跳至 Phase 2 Step 5。
3. Write 依 `rules/實作-規範.md` **只寫剛好讓它通過的程式碼**。
4. Read **執行全部測試確認都通過**;若有測試失敗 → 跳至 Phase 2 Step 3;若呼叫方只指定綠燈 → 跳至 Phase 2 Step 5;若還有這次要做的行為沒有測試 → 跳至 Phase 2 Step 1。
5. Report **列出每個切片的紅綠證據**:測試名稱、紅燈時的失敗訊息與綠燈時的測試結果,以及這一輪記下的重構清單;若呼叫方指定了紅燈或綠燈 → 結束。

## Phase 3: 在綠燈下重構程式碼
1. Read **執行全部測試確認都通過**;若有測試失敗 → 結束。
2. Write 依 `rules/重構-規範.md` **照重構清單做一小步重構**。
3. Read **執行全部測試確認都通過**;若有測試失敗 → 跳至 Phase 3 Step 2;若重構清單還有沒做的項目 → 跳至 Phase 3 Step 2。
4. Report **列出每一步重構與前後的測試結果**。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出接縫清單"]
        P1S1["1. Read：這次會動到<br/>的程式碼與既有測試"]
        G_P1S1_1{"呼叫方指定了紅燈與<br/>testplan.md 的案例？"}
        G_P1S1_2{"呼叫方指定了綠燈與<br/>testplan.md 的案例？"}
        G_P1S1_3{"呼叫方指定了重構？"}
        P1S2["2. Think：列出這次要測的接縫"]
        P1S3["3. Ask：提出接縫清單"]
        G_P1S3_1{"使用者要修改？"}
    end
    subgraph P2["Phase 2: 逐片紅綠實作功能"]
        P2S1["1. Write：寫一個測試"]
        P2S2["2. Read：執行這個測<br/>試確認它是斷言失敗"]
        G_P2S2_1{"它不是斷言失敗？"}
        G_P2S2_2{"呼叫方只指定紅燈？"}
        P2S3["3. Write：只寫剛好讓它通過的程式碼"]
        P2S4["4. Read：執行全部測試確認都通過"]
        G_P2S4_1{"有測試失敗？"}
        G_P2S4_2{"呼叫方只指定綠燈？"}
        G_P2S4_3{"還有這次要做的<br/>行為沒有測試？"}
        P2S5["5. Report：列出每個切片的紅綠證據"]
        G_P2S5_1{"呼叫方指定了紅燈或綠燈？"}
    end
    subgraph P3["Phase 3: 在綠燈下重構程式碼"]
        P3S1["1. Read：執行全部測試確認都通過"]
        G_P3S1_1{"有測試失敗？"}
        P3S2["2. Write：照重構清單做一小步重構"]
        P3S3["3. Read：執行全部測試確認都通過"]
        G_P3S3_1{"有測試失敗？"}
        G_P3S3_2{"重構清單還有沒做的項目？"}
        P3S4["4. Report：列出每一步<br/>重構與前後的測試結果"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| P2S1
    G_P1S1_1 -->|否| G_P1S1_2
    G_P1S1_2 -->|是| P2S3
    G_P1S1_2 -->|否| G_P1S1_3
    G_P1S1_3 -->|是| P3S1
    G_P1S1_3 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| P1S2
    G_P1S3_1 -->|否| P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P2S1
    G_P2S2_1 -->|否| G_P2S2_2
    G_P2S2_2 -->|是| P2S5
    G_P2S2_2 -->|否| P2S3
    P2S3 --> P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P2S3
    G_P2S4_1 -->|否| G_P2S4_2
    G_P2S4_2 -->|是| P2S5
    G_P2S4_2 -->|否| G_P2S4_3
    G_P2S4_3 -->|是| P2S1
    G_P2S4_3 -->|否| P2S5
    P2S5 --> G_P2S5_1
    G_P2S5_1 -->|是| End
    G_P2S5_1 -->|否| P3S1
    P3S1 --> G_P3S1_1
    G_P3S1_1 -->|是| End
    G_P3S1_1 -->|否| P3S2
    P3S2 --> P3S3
    P3S3 --> G_P3S3_1
    G_P3S3_1 -->|是| P3S2
    G_P3S3_1 -->|否| G_P3S3_2
    G_P3S3_2 -->|是| P3S2
    G_P3S3_2 -->|否| P3S4
    P3S4 --> End
```
</details>
