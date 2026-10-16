---
name: artifact-to-skill-engineering
description: 手上有一份別人的 artifact 或規格格式、想做一支能穩定產出同款 artifact 的 Skill 時,用這支 Skill 先把參考範例客製化到滿意,再抽成骨架與範例,最後交給 skill-engineering 後設出 SOP 與規則;使用者提到 artifact、照這個範例做一支 skill、從範例反推 skill、抽樣板、artifact to skill 時使用。(未驗證)
---

# SOP

## Phase 1: 選定參考範例
1. Read 依 `rules/參考範例-規範.md` **使用者的請求**;若已講明要參考哪一份 artifact、目標 Skill 叫什麼、放在哪裡 → 跳至 Phase 1 Step 3。
2. Ask **問參考範例的實物與目標 Skill**:參考 artifact 的檔案路徑、網址或貼上的全文,目標 Skill 叫什麼、放在哪裡。
3. Write 建立目標 Skill 的資料夾,`SKILL.md` 先只寫 frontmatter 的 name,**把參考範例寫成目標 Skill 的範例**,全文放在 `templates/` 底下。

## Phase 2: 客製化範例
1. Think **列出範例和使用者需求對不上的地方**,每一處附上建議的改法。
2. Ask **一次提出一處修改與建議**,問使用者要不要改、怎麼改。
3. Write **把使用者同意的修改改進範例**;若還有沒問過的地方 → 跳至 Phase 2 Step 2。
4. Ask **提出改好的範例**,問使用者是否滿意;若使用者要修改 → 跳至 Phase 2 Step 1。

## Phase 3: 抽出樣板
1. Delegate 轉交 skill-form-template,**把改好的範例抽成骨架與範例**;若使用者已講明範例輸入 → 跳至 Phase 4 Step 2。

## Phase 4: 寫出目標 Skill
1. Ask **問目標 Skill 的範例輸入**:使用者之後會交給它的一段輸入。
2. Delegate 轉交 skill-engineering,以骨架與範例為驗收產出、範例輸入為驗收輸入,**寫出目標 Skill**。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 選定參考範例"]
        P1S1["1. Read：使用者的請求"]
        G_P1S1_1{"已講明要參考哪一份<br/>artifact、目標 Skill<br/>叫什麼、放在哪裡？"}
        P1S2["2. Ask：問參考範例的實物與目標 Skill"]
        P1S3["3. Write：把參考範例<br/>寫成目標 Skill 的範例"]
    end
    subgraph P2["Phase 2: 客製化範例"]
        P2S1["1. Think：列出範例和使<br/>用者需求對不上的地方"]
        P2S2["2. Ask：一次提出一處修改與建議"]
        P2S3["3. Write：把使用者同意的修改改進範例"]
        G_P2S3_1{"還有沒問過的地方？"}
        P2S4["4. Ask：提出改好的範例"]
        G_P2S4_1{"使用者要修改？"}
    end
    subgraph P3["Phase 3: 抽出樣板"]
        P3S1["1. Delegate：把改好<br/>的範例抽成骨架與範例"]
        G_P3S1_1{"使用者已講明範例輸入？"}
    end
    subgraph P4["Phase 4: 寫出目標 Skill"]
        P4S1["1. Ask：問目標 Skill 的範例輸入"]
        P4S2["2. Delegate：寫出目標 Skill"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| P1S3
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P2S2
    G_P2S3_1 -->|否| P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P2S1
    G_P2S4_1 -->|否| P3S1
    P3S1 --> G_P3S1_1
    G_P3S1_1 -->|是| P4S2
    G_P3S1_1 -->|否| P4S1
    P4S1 --> P4S2
    P4S2 --> End
```

```mermaid
sequenceDiagram
    actor User
    participant Main as artifact-to-skill-engineering
    participant Sub_1 as skill-form-template
    participant Sub_2 as skill-engineering
    Note over User,Sub_2: Phase 1: 選定參考範例
    Main->>User: 2. Ask：問參考範例的實物與目標 Skill
    User-->>Main: 回覆確認
    Note over User,Sub_2: Phase 2: 客製化範例
    Main->>User: 2. Ask：一次提出一處修改與建議
    User-->>Main: 回覆確認
    Main->>User: 4. Ask：提出改好的範例
    User-->>Main: 回覆確認
    Note over User,Sub_2: Phase 3: 抽出樣板
    Main->>Sub_1: 1. Delegate：把改好的範例抽成骨架與範例
    Sub_1-->>Main: 完成並交回產出
    Note over User,Sub_2: Phase 4: 寫出目標 Skill
    Main->>User: 1. Ask：問目標 Skill 的範例輸入
    User-->>Main: 回覆確認
    Main->>Sub_2: 2. Delegate：寫出目標 Skill
    Sub_2-->>Main: 完成並交回產出
```
</details>
