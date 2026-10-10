---
name: skill-derive-rule
description: 給定一支已經寫好的 SOP skill,使用者想針對其中某個步驟,展開該步驟需要遵守的規則時,就必須使用此 Skill。使用者因既有 Skill 的產出不符預期而要求修改時,先用 skill-engineering 分析根因,即使已指定步驟或修法亦同;依已確認方案轉交本 Skill 執行時,直接承接。(未驗證)
---

# SOP

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出展開後的樣子"]
        P1S1["1. Read：目標 skill 的 SKILL.md 與已有的 Rule…"]
        G_P1S1_1{"使用者已講明要展開哪一步、要把關什麼？"}
        P1S2["2. Ask：問使用者要展開哪一步(Phase N Step M)、這一…"]
        P1S3["3. Think：決定展開後的樣子:要加哪幾條 Rule、落在哪個 Rule…"]
        G_P1S3_1{"決定不展開？"}
        G_P1S3_2{"符合〈沿用已確認的具體轉換〉？"}
        P1S4["4. Ask：提出展開後的樣子,問使用者是否可以寫入"]
        G_P1S4_1{"使用者要修改？"}
    end
    subgraph P2["Phase 2: 展開 Rule File"]
        P2S1["1. Delegate：轉交 skill-form-rule,把使用者要把關的事寫…"]
        G_P2S1_1{"步驟寫法不變？"}
    end
    subgraph P3["Phase 3: 改寫指定步驟"]
        P3S1["1. Delegate：轉交 skill-form-sop,把指定那一步改成展開後…"]
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
    participant Main as skill-derive-rule
    participant Sub_1 as skill-form-rule
    participant Sub_2 as skill-form-sop
    Main->>User: P1S2 依 rules/提問-規範.md 問使用者要展開哪一步(P…
    User-->>Main: 回覆確認
    Main->>User: P1S4 提出展開後的樣子,問使用者是否可以寫入
    User-->>Main: 回覆確認
    Main->>Sub_1: P2S1 轉交 skill-form-rule,把使用者要把關的事寫成那個 R…
    Sub_1-->>Main: 完成並交回產出
    Main->>Sub_2: P3S1 轉交 skill-form-sop,把指定那一步改成展開後的寫法
    Sub_2-->>Main: 完成並交回產出
```
</details>

## Phase 1: 提出展開後的樣子
1. Read 目標 skill 的 SKILL.md 與已有的 Rule File;若使用者已講明要展開哪一步、要把關什麼 → 跳至 Phase 1 Step 3。
2. Ask 依 `rules/提問-規範.md` 問使用者要展開哪一步(Phase N Step M)、這一步要把關什麼。
3. Think 依 `rules/展開-規範.md` 決定展開後的樣子:要加哪幾條 Rule、落在哪個 Rule File、指定那一步改成什麼寫法;若決定不展開 → 結束;若符合〈沿用已確認的具體轉換〉 → 跳至 Phase 2 Step 1。
4. Ask 提出展開後的樣子,問使用者是否可以寫入;若使用者要修改 → 跳至 Phase 1 Step 3。

## Phase 2: 展開 Rule File
1. Delegate 轉交 skill-form-rule,把使用者要把關的事寫成那個 Rule File 的 Rule;若指定那一步的寫法不變 → 結束。

## Phase 3: 改寫指定步驟
1. Delegate 轉交 skill-form-sop,把指定那一步改成展開後的寫法。
