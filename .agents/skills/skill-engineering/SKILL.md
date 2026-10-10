---
name: skill-engineering
description: 要創建一支全新的 Skill,或使用者對既有 Skill 跑出來的結果不滿意、要修改或優化它時,就必須使用此 Skill(未驗證)
---

# SOP

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出根因報告"]
        P1S1["1. Read：問題發生時的對話與當時用到的每一支 Skill 的整個資料夾"]
        G_P1S1_1{"創建全新 Skill？"}
        G_P1S1_2{"已有輸入與產出？"}
        P1S2["2. Ask：問使用者那一次交給 Skill 的輸入與它交出的產出"]
        P1S3["3. Think：用當時的輸入逐步演練每一支 Skill 的 SOP 找出根因"]
        P1S4["4. Ask：提出根因報告,問使用者是否同意"]
        G_P1S4_1{"使用者不同意？"}
        G_P1S4_2{"落差皆不歸類？"}
    end
    subgraph P2["Phase 2: 提出藍圖"]
        P2S1["1. Think：決定目標 Skill 的藍圖:產出鏈、主幹、變更與新掛部位…"]
        P2S2["2. Ask：提出藍圖,問使用者是否可以寫入"]
        G_P2S2_1{"使用者要修改？"}
    end
    subgraph P3["Phase 3: 寫出主幹"]
        P3S1["1. Write：把目標 Skill 的 SKILL.md frontmat…"]
        G_P3S1_1{"藍圖的主幹和現況的 # SOP 相同？"}
        P3S2["2. Delegate：轉交 skill-form-sop,把目標 Skill 的…"]
    end
    subgraph P4["Phase 4: 寫出部位"]
        P4S1["1. Write：刪除藍圖裡整個檔列為刪的檔"]
        P4S2["2. Delegate：轉交 skill-form-rule、skill-form…"]
        G_P4S2_1{"內容與藍圖不同？"}
        P4S3["3. Delegate：替藍圖裡每一個新掛的部位轉交 skill-derive-r…"]
        G_P4S3_1{"內容與藍圖不同？"}
    end
    subgraph P5["Phase 5: 列出驗收紀錄"]
        P5S1["1. Write：替藍圖的每一列驗收輸入,把實跑會改到的檔複製到 tmp/v…"]
        P5S2["2. Delegate：把每一列驗收輸入與它的複本交給不帶這場對話脈絡的 suba…"]
        P5S3["3. Read：每一份複本和原本的差異與交出的腳本執行的結果"]
        P5S4["4. Think：比對每一份實跑結果"]
        G_P5S4_1{"驗收對不上？"}
        P5S5["5. Ask：在給使用者的回覆裡列出驗收紀錄"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| P2S1
    G_P1S1_1 -->|否| G_P1S1_2
    G_P1S1_2 -->|是| P1S3
    G_P1S1_2 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> P1S4
    P1S4 --> G_P1S4_1
    G_P1S4_1 -->|是| P1S3
    G_P1S4_1 -->|否| G_P1S4_2
    G_P1S4_2 -->|是| End
    G_P1S4_2 -->|否| P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P2S1
    G_P2S2_1 -->|否| P3S1
    P3S1 --> G_P3S1_1
    G_P3S1_1 -->|是| P4S1
    G_P3S1_1 -->|否| P3S2
    P3S2 --> P4S1
    P4S1 --> P4S2
    P4S2 --> G_P4S2_1
    G_P4S2_1 -->|是| P2S1
    G_P4S2_1 -->|否| P4S3
    P4S3 --> G_P4S3_1
    G_P4S3_1 -->|是| P2S1
    G_P4S3_1 -->|否| P5S1
    P5S1 --> P5S2
    P5S2 --> P5S3
    P5S3 --> P5S4
    P5S4 --> G_P5S4_1
    G_P5S4_1 -->|是| P2S1
    G_P5S4_1 -->|否| P5S5
    P5S5 --> End
```

```mermaid
sequenceDiagram
    actor User
    participant Main as skill-engineering
    participant Sub_1 as skill-form-sop
    participant Sub_2 as skill-form-rule
    participant Sub_3 as skill-form-template
    participant Sub_4 as skill-form-script
    participant Sub_5 as skill-derive-rule
    participant Sub_6 as skill-derive-template
    participant Sub_7 as skill-derive-script
    Main->>User: P1S2 問使用者那一次交給 Skill 的輸入與它交出的產出
    User-->>Main: 回覆確認
    Main->>User: P1S4 依骨架 templates/根因報告.md 與範例 tem…
    User-->>Main: 回覆確認
    Main->>User: P2S2 依骨架 templates/藍圖.md 與範例 templ…
    User-->>Main: 回覆確認
    Main->>Sub_1: P3S2 轉交 skill-form-sop,把目標 Skill 的 # SO…
    Sub_1-->>Main: 完成並交回產出
    Note over Main: P4S2 委派分流：skill-form-rule、skill-form-template 或 s…
    Note over Main: P4S3 委派分流：skill-derive-rule、skill-derive-template…
    Main->>User: P5S5 依骨架 templates/驗收紀錄.md 與範例 tem…
    User-->>Main: 回覆確認
```
</details>

## Phase 1: 提出根因報告
1. Read 問題發生時的對話與當時用到的每一支 Skill 的整個資料夾;若要創建的是全新的 Skill → 跳至 Phase 2 Step 1;若對話裡有那一次交給 Skill 的輸入與它交出的產出 → 跳至 Phase 1 Step 3。
2. Ask 問使用者那一次交給 Skill 的輸入與它交出的產出。
3. Think 依 `rules/根因-規範.md` 用當時的輸入逐步演練每一支 Skill 的 SOP 找出根因。
4. Ask 依骨架 `templates/根因報告.md` 與範例 `templates/根因報告.example.md` 提出根因報告,問使用者是否同意;若使用者不同意 → 跳至 Phase 1 Step 3;若使用者同意,而每一個落差都不歸類 → 結束。

## Phase 2: 提出藍圖
1. Think 依 `rules/藍圖-規範.md` 決定目標 Skill 的藍圖:產出鏈、主幹、變更與新掛部位的樣子。
2. Ask 依骨架 `templates/藍圖.md` 與範例 `templates/藍圖.example.md` 提出藍圖,問使用者是否可以寫入;若使用者要修改 → 跳至 Phase 2 Step 1。

## Phase 3: 寫出主幹
1. Write 把目標 Skill 的 `SKILL.md` frontmatter 寫成藍圖的 name 與 description;若藍圖的主幹和現況的 `# SOP` 相同 → 跳至 Phase 4 Step 1。
2. Delegate 轉交 skill-form-sop,把目標 Skill 的 `# SOP` 寫成藍圖的主幹。

## Phase 4: 寫出部位
1. Write 刪除藍圖裡整個檔列為刪的檔。
2. Delegate 轉交 skill-form-rule、skill-form-template 或 skill-form-script,把藍圖裡有變更的既有檔改寫成終態;若寫出來的內容和藍圖不同 → 跳至 Phase 2 Step 1。
3. Delegate 替藍圖裡每一個新掛的部位轉交 skill-derive-rule、skill-derive-template 或 skill-derive-script,一次掛一步;若掛上去的內容和藍圖不同 → 跳至 Phase 2 Step 1。

## Phase 5: 列出驗收紀錄
1. Write 替藍圖的每一列驗收輸入,把實跑會改到的檔複製到 `tmp/verify/` 底下各自的資料夾。
2. Delegate 依骨架 `templates/實跑指示.md` 與範例 `templates/實跑指示.example.md` 把每一列驗收輸入與它的複本交給不帶這場對話脈絡的 subagent,實跑寫完的目標 Skill。
3. Read 每一份複本和原本的差異與交出的腳本執行的結果。
4. Think 比對每一份實跑結果;若驗收紀錄裡有一列判定為對不上 → 跳至 Phase 2 Step 1。
5. Ask 依骨架 `templates/驗收紀錄.md` 與範例 `templates/驗收紀錄.example.md` 在給使用者的回覆裡列出驗收紀錄。
