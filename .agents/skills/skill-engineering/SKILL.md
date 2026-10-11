---
name: skill-engineering
description: 要創建一支全新的 Skill,或使用者對既有 Skill 跑出來的結果不滿意、要修改或優化它時,就必須使用此 Skill(未驗證)
---

# SOP

## Phase 1: 提出根因報告
1. Read **問題發生時的現場**:當時的對話與用到的每一支 Skill 的整個資料夾;若要創建的是全新的 Skill → 跳至 Phase 2 Step 1;若對話裡有那次交給 Skill 的輸入與交出的產出 → 跳至 Phase 1 Step 3。
2. Ask 問使用者**那次交給 Skill 的輸入與交出的產出**。
3. Think 依 `rules/根因-規範.md` 用當時的輸入逐步演練每一支 Skill 的 SOP **找出根因**。
4. Ask 依骨架 `templates/根因報告.md` 與範例 `templates/根因報告.example.md` **提出根因報告**,問使用者是否同意;若使用者不同意 → 跳至 Phase 1 Step 3;若使用者同意,而每一個落差都不歸類 → 結束。

## Phase 2: 提出藍圖
1. Think 依 `rules/藍圖-規範.md` **決定目標 Skill 的藍圖**:產出鏈、主幹、變更與新掛部位的樣子。
2. Ask 依骨架 `templates/藍圖.md` 與範例 `templates/藍圖.example.md` **提出藍圖**,問使用者是否可以寫入;若使用者要修改 → 跳至 Phase 2 Step 1。

## Phase 3: 寫出主幹
1. Write 把目標 Skill 的 `SKILL.md` frontmatter **寫成藍圖的 name 與 description**;若藍圖的主幹和現況的 `# SOP` 相同 → 跳至 Phase 4 Step 1。
2. Delegate 轉交 skill-form-sop,把目標 Skill 的 `# SOP` **寫成藍圖的主幹**。

## Phase 4: 寫出部位
1. Write **刪除藍圖裡整個檔列為刪的檔**。
2. Delegate 轉交 skill-form-rule、skill-form-template 或 skill-form-script,**把藍圖裡有變更的既有檔改寫成終態**;若寫出來的內容和藍圖不同 → 跳至 Phase 2 Step 1。
3. Delegate 轉交 skill-derive-rule、skill-derive-template 或 skill-derive-script,**把藍圖裡每一個新掛的部位掛上去**,一次掛一步;若掛上去的內容和藍圖不同 → 跳至 Phase 2 Step 1。

## Phase 5: 列出驗收紀錄
1. Write 替還沒有實跑的每一列驗收輸入與每一種要查證的讀法,**把實跑會改到的檔複製到 `tmp/verify/`** 底下各自的資料夾。
2. Delegate 依骨架 `templates/實跑指示.md` 與範例 `templates/實跑指示.example.md` 把這些驗收輸入、要查證的讀法與各自的複本交給不帶這場對話脈絡的 subagent,**實跑寫完的目標 Skill**。
3. Read **每一份實跑的結果**:複本和原本的差異、交出的腳本執行的結果。
4. Think **比對每一份實跑結果**;若驗收紀錄裡有一列判定為對不上 → 跳至 Phase 2 Step 1;若有一種還沒有實跑過的讀法照著做會讓使用者的請求交不出來 → 跳至 Phase 5 Step 1。
5. Report 依骨架 `templates/驗收紀錄.md` 與範例 `templates/驗收紀錄.example.md` 在給使用者的回覆裡**列出驗收紀錄**。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出根因報告"]
        P1S1["1. Read：問題發生時的現場"]
        G_P1S1_1{"創建全新 Skill？"}
        G_P1S1_2{"已有輸入與產出？"}
        P1S2["2. Ask：那次交給 Skill<br/>的輸入與交出的產出"]
        P1S3["3. Think：找出根因"]
        P1S4["4. Ask：提出根因報告"]
        G_P1S4_1{"使用者不同意？"}
        G_P1S4_2{"落差皆不歸類？"}
    end
    subgraph P2["Phase 2: 提出藍圖"]
        P2S1["1. Think：決定目標 Skill 的藍圖"]
        P2S2["2. Ask：提出藍圖"]
        G_P2S2_1{"使用者要修改？"}
    end
    subgraph P3["Phase 3: 寫出主幹"]
        P3S1["1. Write：寫成藍圖的<br/>name 與 description"]
        G_P3S1_1{"藍圖的主幹和現況<br/>的 # SOP 相同？"}
        P3S2["2. Delegate：寫成藍圖的主幹"]
    end
    subgraph P4["Phase 4: 寫出部位"]
        P4S1["1. Write：刪除藍圖裡整個檔列為刪的檔"]
        P4S2["2. Delegate：把藍圖裡有<br/>變更的既有檔改寫成終態"]
        G_P4S2_1{"內容與藍圖不同？"}
        P4S3["3. Delegate：把藍圖裡<br/>每一個新掛的部位掛上去"]
        G_P4S3_1{"內容與藍圖不同？"}
    end
    subgraph P5["Phase 5: 列出驗收紀錄"]
        P5S1["1. Write：把實跑會改到<br/>的檔複製到 tmp/verify/"]
        P5S2["2. Delegate：實跑寫完的目標 Skill"]
        P5S3["3. Read：每一份實跑的結果"]
        P5S4["4. Think：比對每一份實跑結果"]
        G_P5S4_1{"驗收對不上？"}
        G_P5S4_2{"有一種還沒有實跑過的<br/>讀法照著做會讓使用者<br/>的請求交不出來？"}
        P5S5["5. Report：列出驗收紀錄"]
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
    G_P5S4_1 -->|否| G_P5S4_2
    G_P5S4_2 -->|是| P5S1
    G_P5S4_2 -->|否| P5S5
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
    Note over User,Sub_7: Phase 1: 提出根因報告
    Main->>User: 2. Ask：那次交給 Skill 的輸入與交出的產出
    User-->>Main: 回覆確認
    Main->>User: 4. Ask：提出根因報告
    User-->>Main: 回覆確認
    Note over User,Sub_7: Phase 2: 提出藍圖
    Main->>User: 2. Ask：提出藍圖
    User-->>Main: 回覆確認
    Note over User,Sub_7: Phase 3: 寫出主幹
    Main->>Sub_1: 2. Delegate：寫成藍圖的主幹
    Sub_1-->>Main: 完成並交回產出
    Note over User,Sub_7: Phase 4: 寫出部位
    alt skill-form-rule
        Main->>Sub_2: 2. Delegate：把藍圖裡有變更的既有檔改寫成終態
        Sub_2-->>Main: 完成並交回產出
    else skill-form-template
        Main->>Sub_3: 2. Delegate：把藍圖裡有變更的既有檔改寫成終態
        Sub_3-->>Main: 完成並交回產出
    else skill-form-script
        Main->>Sub_4: 2. Delegate：把藍圖裡有變更的既有檔改寫成終態
        Sub_4-->>Main: 完成並交回產出
    end
    alt skill-derive-rule
        Main->>Sub_5: 3. Delegate：把藍圖裡每一個新掛的部位掛上去
        Sub_5-->>Main: 完成並交回產出
    else skill-derive-template
        Main->>Sub_6: 3. Delegate：把藍圖裡每一個新掛的部位掛上去
        Sub_6-->>Main: 完成並交回產出
    else skill-derive-script
        Main->>Sub_7: 3. Delegate：把藍圖裡每一個新掛的部位掛上去
        Sub_7-->>Main: 完成並交回產出
    end
    Note over User,Sub_7: Phase 5: 列出驗收紀錄
    Main->>User: 5. Report：列出驗收紀錄
```
</details>
