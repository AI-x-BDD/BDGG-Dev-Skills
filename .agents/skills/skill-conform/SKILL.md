---
name: skill-conform
description: 改了 skill-form-sop、skill-form-rule、skill-form-template 或 skill-form-script 的規範之後,要讓既有的 Skill 符合現行規範時,用這支 Skill 檢查指定的 Skill、把不過的部位轉交對應的 form skill 改寫並重新檢查;使用者提到規範遷移、符合規範、重新處理 SKILL.md、檢查所有 skill、conform、migrate 時使用。(未驗證)
---

# SOP

## Phase 1: 提出檢查清單
1. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_skills.py --skills <放 Skill 的目錄>` **取得每一支 Skill 的檢查結果**;若每一項都過且沒有候選 → 結束。
2. Ask 依骨架 `templates/檢查清單.md` 與範例 `templates/檢查清單.example.md` **提出檢查清單**,問使用者這次要處理哪幾項;若使用者一項都不處理 → 結束。

## Phase 2: 改寫不過的部位
1. Delegate 執行 `uv run scripts/check_skills.py --skills <放 Skill 的目錄> --only <只缺流程視覺圖的 Skill 名稱> --write-diagrams` 替使用者要處理、而且只缺流程視覺圖的 Skill **注入流程視覺圖**;若使用者要處理的項目都只缺流程視覺圖 → 跳至 Phase 2 Step 5。
2. Think 依 `rules/改寫-規範.md` **決定其餘每一項要改成的寫法**。
3. Ask 依骨架 `templates/改寫提案.md` 與範例 `templates/改寫提案.example.md` **提出改寫提案**,問使用者是否可以寫入;若使用者要修改 → 跳至 Phase 2 Step 2。
4. Delegate 轉交 skill-form-sop、skill-form-rule、skill-form-template 或 skill-form-script,**照確認過的寫法改寫**使用者要處理的其餘每一項。
5. Delegate 執行 `uv run scripts/check_skills.py --skills <放 Skill 的目錄> --only <改過的 Skill 名稱>` **取得改過的每支 Skill 重新檢查的結果**;若使用者要處理的項目還有不過 → 跳至 Phase 2 Step 2。

## Phase 3: 列出遷移紀錄
1. Report 依骨架 `templates/遷移紀錄.md` 與範例 `templates/遷移紀錄.example.md` **列出遷移紀錄**。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出檢查清單"]
        P1S1["1. Delegate：取得每一<br/>支 Skill 的檢查結果"]
        G_P1S1_1{"每一項都過且沒有候選？"}
        P1S2["2. Ask：提出檢查清單"]
        G_P1S2_1{"使用者一項都不處理？"}
    end
    subgraph P2["Phase 2: 改寫不過的部位"]
        P2S1["1. Delegate：注入流程視覺圖"]
        G_P2S1_1{"使用者要處理的項目<br/>都只缺流程視覺圖？"}
        P2S2["2. Think：決定其餘每一項要改成的寫法"]
        P2S3["3. Ask：提出改寫提案"]
        G_P2S3_1{"使用者要修改？"}
        P2S4["4. Delegate：照確認過的寫法改寫"]
        P2S5["5. Delegate：取得改過的每<br/>支 Skill 重新檢查的結果"]
        G_P2S5_1{"使用者要處理的<br/>項目還有不過？"}
    end
    subgraph P3["Phase 3: 列出遷移紀錄"]
        P3S1["1. Report：列出遷移紀錄"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| End
    G_P1S1_1 -->|否| P1S2
    P1S2 --> G_P1S2_1
    G_P1S2_1 -->|是| End
    G_P1S2_1 -->|否| P2S1
    P2S1 --> G_P2S1_1
    G_P2S1_1 -->|是| P2S5
    G_P2S1_1 -->|否| P2S2
    P2S2 --> P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P2S2
    G_P2S3_1 -->|否| P2S4
    P2S4 --> P2S5
    P2S5 --> G_P2S5_1
    G_P2S5_1 -->|是| P2S2
    G_P2S5_1 -->|否| P3S1
    P3S1 --> End
```

```mermaid
sequenceDiagram
    actor User
    participant Main as skill-conform
    participant Sub_1 as skill-form-sop
    participant Sub_2 as skill-form-rule
    participant Sub_3 as skill-form-template
    participant Sub_4 as skill-form-script
    Note over User,Sub_4: Phase 1: 提出檢查清單
    Main->>User: 2. Ask：提出檢查清單
    User-->>Main: 回覆確認
    Note over User,Sub_4: Phase 2: 改寫不過的部位
    Main->>User: 3. Ask：提出改寫提案
    User-->>Main: 回覆確認
    alt skill-form-sop
        Main->>Sub_1: 4. Delegate：照確認過的寫法改寫
        Sub_1-->>Main: 完成並交回產出
    else skill-form-rule
        Main->>Sub_2: 4. Delegate：照確認過的寫法改寫
        Sub_2-->>Main: 完成並交回產出
    else skill-form-template
        Main->>Sub_3: 4. Delegate：照確認過的寫法改寫
        Sub_3-->>Main: 完成並交回產出
    else skill-form-script
        Main->>Sub_4: 4. Delegate：照確認過的寫法改寫
        Sub_4-->>Main: 完成並交回產出
    end
    Note over User,Sub_4: Phase 3: 列出遷移紀錄
    Main->>User: 1. Report：列出遷移紀錄
```
</details>
