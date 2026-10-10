---
name: skill-conform
description: 改了 skill-form-sop、skill-form-rule、skill-form-template 或 skill-form-script 的規範之後,要讓既有的 Skill 符合現行規範時,用這支 Skill 檢查指定的 Skill、把不過的部位轉交對應的 form skill 改寫並重新檢查;使用者提到規範遷移、符合規範、重新處理 SKILL.md、檢查所有 skill、conform、migrate 時使用。(未驗證)
---

# SOP

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出檢查清單"]
        P1S1["1. Delegate：取得每一支 Skill 的檢查結果"]
        G_P1S1_1{"每一項都過且沒有候選？"}
        P1S2["2. Ask：提出檢查清單,問使用者這次要處理哪幾項"]
        G_P1S2_1{"使用者一項都不處理？"}
    end
    subgraph P2["Phase 2: 改寫不過的部位"]
        P2S1["1. Delegate：替使用者要處理、而且只缺流程視覺圖的 Skill 注入流程…"]
        G_P2S1_1{"使用者要處理的項目都只缺流程視覺圖？"}
        P2S2["2. Think：決定其餘每一項要改成的寫法"]
        P2S3["3. Ask：提出改寫提案,問使用者是否可以寫入"]
        G_P2S3_1{"使用者要修改？"}
        P2S4["4. Delegate：轉交 skill-form-sop、skill-form-…"]
        P2S5["5. Delegate：取得改過的每一支 Skill 重新檢查的結果"]
        G_P2S5_1{"使用者要處理的項目還有不過？"}
    end
    subgraph P3["Phase 3: 列出遷移紀錄"]
        P3S1["1. Think：列出遷移紀錄"]
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
    Main->>User: P1S2 依骨架 templates/檢查清單.md 與範例 tem…
    User-->>Main: 回覆確認
    Main->>User: P2S3 依骨架 templates/改寫提案.md 與範例 tem…
    User-->>Main: 回覆確認
    Note over Main: P2S4 委派分流：skill-form-sop、skill-form-rule、skill-fo…
```
</details>

## Phase 1: 提出檢查清單
1. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_skills.py --skills <放 Skill 的目錄>` 取得每一支 Skill 的檢查結果;若每一項都過且沒有候選 → 結束。
2. Ask 依骨架 `templates/檢查清單.md` 與範例 `templates/檢查清單.example.md` 提出檢查清單,問使用者這次要處理哪幾項;若使用者一項都不處理 → 結束。

## Phase 2: 改寫不過的部位
1. Delegate 執行 `uv run scripts/check_skills.py --skills <放 Skill 的目錄> --only <只缺流程視覺圖的 Skill 名稱> --write-diagrams` 替使用者要處理、而且只缺流程視覺圖的 Skill 注入流程視覺圖;若使用者要處理的項目都只缺流程視覺圖 → 跳至 Phase 2 Step 5。
2. Think 決定其餘每一項要改成的寫法。
3. Ask 依骨架 `templates/改寫提案.md` 與範例 `templates/改寫提案.example.md` 提出改寫提案,問使用者是否可以寫入;若使用者要修改 → 跳至 Phase 2 Step 2。
4. Delegate 轉交 skill-form-sop、skill-form-rule、skill-form-template 或 skill-form-script,照確認過的寫法改寫使用者要處理的其餘每一項。
5. Delegate 執行 `uv run scripts/check_skills.py --skills <放 Skill 的目錄> --only <改過的 Skill 名稱>` 取得改過的每一支 Skill 重新檢查的結果;若使用者要處理的項目還有不過 → 跳至 Phase 2 Step 2。

## Phase 3: 列出遷移紀錄
1. Think 依骨架 `templates/遷移紀錄.md` 與範例 `templates/遷移紀錄.example.md` 列出遷移紀錄。
