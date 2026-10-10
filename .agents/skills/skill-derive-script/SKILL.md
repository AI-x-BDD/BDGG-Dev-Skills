---
name: skill-derive-script
description: 給定一支已經寫好的 SOP skill,使用者想針對其中某個步驟,把該步驟的職責委派給 Python 腳本執行時,就必須使用此 Skill。使用者因既有 Skill 的產出不符預期而要求修改時,先用 skill-engineering 分析根因,即使已指定步驟或修法亦同;依已確認方案轉交本 Skill 執行時,直接承接。(未驗證)
---

# SOP

## Phase 1: 提出委派後的樣子
1. Read 目標 skill 的 **SKILL.md 與 `scripts/` 底下已有的腳本**;若使用者已講明要委派哪一步、腳本吃什麼吐什麼 → 跳至 Phase 1 Step 3。
2. Ask 依 `rules/提問-規範.md` **問要委派哪一步、腳本吃什麼吐什麼**(哪一步寫成 Phase N Step M)。
3. Think 依 `rules/委派-規範.md` **決定委派後的樣子**:腳本檔名、參數與輸出、第三方套件、指定那一步改成什麼寫法;若決定不委派 → 結束;若符合〈沿用已確認的具體轉換〉 → 跳至 Phase 2 Step 1。
4. Ask **提出委派後的樣子**,問使用者是否可以寫入;若使用者要修改 → 跳至 Phase 1 Step 3。

## Phase 2: 寫出腳本
1. Delegate 轉交 skill-form-script,**把那一步的職責寫成腳本**;若指定那一步的寫法不變 → 結束。

## Phase 3: 改寫指定步驟
1. Delegate 轉交 skill-form-sop,**把指定那一步改成委派後的寫法**。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出委派後的樣子"]
        P1S1["1. Read：SKILL.md 與<br/>scripts/ 底下已有的腳本"]
        G_P1S1_1{"使用者已講明要委派哪一<br/>步、腳本吃什麼吐什麼？"}
        P1S2["2. Ask：問要委派哪一<br/>步、腳本吃什麼吐什麼"]
        P1S3["3. Think：決定委派後的樣子"]
        G_P1S3_1{"決定不委派？"}
        G_P1S3_2{"符合〈沿用已確認<br/>的具體轉換〉？"}
        P1S4["4. Ask：提出委派後的樣子"]
        G_P1S4_1{"使用者要修改？"}
    end
    subgraph P2["Phase 2: 寫出腳本"]
        P2S1["1. Delegate：把那一步的職責寫成腳本"]
        G_P2S1_1{"步驟寫法不變？"}
    end
    subgraph P3["Phase 3: 改寫指定步驟"]
        P3S1["1. Delegate：把指定那<br/>一步改成委派後的寫法"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| P1S3
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| End
    G_P1S3_1 -->|否| G_P1S3_2
    G_P1S3_2 -->|是| P2S1
    G_P1S3_2 -->|否| P1S4
    P1S4 --> G_P1S4_1
    G_P1S4_1 -->|是| P1S3
    G_P1S4_1 -->|否| P2S1
    P2S1 --> G_P2S1_1
    G_P2S1_1 -->|是| End
    G_P2S1_1 -->|否| P3S1
    P3S1 --> End
```

```mermaid
sequenceDiagram
    actor User
    participant Main as skill-derive-script
    participant Sub_1 as skill-form-script
    participant Sub_2 as skill-form-sop
    Note over User,Sub_2: Phase 1: 提出委派後的樣子
    Main->>User: 2. Ask：問要委派哪一步、腳本吃什麼吐什麼
    User-->>Main: 回覆確認
    Main->>User: 4. Ask：提出委派後的樣子
    User-->>Main: 回覆確認
    Note over User,Sub_2: Phase 2: 寫出腳本
    Main->>Sub_1: 1. Delegate：把那一步的職責寫成腳本
    Sub_1-->>Main: 完成並交回產出
    Note over User,Sub_2: Phase 3: 改寫指定步驟
    Main->>Sub_2: 1. Delegate：把指定那一步改成委派後的寫法
    Sub_2-->>Main: 完成並交回產出
```
</details>
