---
name: double-diamond-principle
description: 收到新的功能需求、需求模糊或有多種解讀、要在多個方案之間做選擇、或動手寫程式之前,用這支 Skill 依雙鑽石(Double Diamond)流程走過探查問題現況(Discover)、確立問題簡報(Define)、比較候選方案(Develop)與交付驗收成果(Deliver);使用者提到幫我開發、幫我做一個、我想加一個功能、這個要怎麼設計、雙鑽石、double diamond、需求探索、問題定義、先釐清需求時使用。(未驗證)
---

# SOP

## Phase 1: 探查問題現況
1. Read 讀取需求、相關程式碼、既有行為、測試與相關文件。
2. Think 依 `rules/探查-規範.md` 梳理受影響的人、現況行為、已確認事實與未確認假設。
3. Ask **向使用者確認關鍵疑問與未確認假設**;若使用者不在線上 → 跳至 Phase 2 Step 1。

## Phase 2: 確立問題簡報
1. Think 依 `rules/簡報-規範.md` 將洞察收斂成包含問題陳述、範圍內外、成功準則與限制的問題簡報。
2. Ask **提出問題簡報**並向使用者確認問題定義與範圍;若使用者要修改 → 跳至 Phase 2 Step 1;若根本問題改變 → 跳至 Phase 1 Step 1。

## Phase 3: 比較候選方案
1. Think 依 `rules/方案-規範.md` 針對問題簡報**提出至少兩個具實質差異的做法**並評估取捨。
2. Ask **提出候選方案比較**並請使用者確認做法;若需要重新定義問題 → 跳至 Phase 2 Step 1。

## Phase 4: 交付驗收成果
1. Think 依 `rules/交付-規範.md` **設計小規模測試**驗證方案中最不確定之處;若選定方案可以直接進入完整實作 → 跳至 Phase 4 Step 3。
2. Write **實作驗證切片**並確認驗證結果;若方案行不通 → 跳至 Phase 3 Step 1。
3. Write **完成選定方案的完整實作與測試**。
4. Read **執行完整驗證並確認成功準則**。
5. Ask 依骨架 `templates/雙鑽石紀錄.md` 與範例 `templates/雙鑽石紀錄.example.md` **提出雙鑽石紀錄與成果回報**並等使用者確認;若實作中發現需求需修正 → 跳至 Phase 2 Step 1。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 探查問題現況"]
        P1S1["1. Read：讀取需求、相關程式<br/>碼、既有行為、測試與相關文件"]
        P1S2["2. Think：梳理受影響的人、現況<br/>行為、已確認事實與未確認假設"]
        P1S3["3. Ask：向使用者確認<br/>關鍵疑問與未確認假設"]
        G_P1S3_1{"使用者不在線上？"}
    end
    subgraph P2["Phase 2: 確立問題簡報"]
        P2S1["1. Think：將洞察收斂成包含問題陳述、<br/>範圍內外、成功準則與限制的問題簡報"]
        P2S2["2. Ask：提出問題簡報"]
        G_P2S2_1{"使用者要修改？"}
        G_P2S2_2{"根本問題改變？"}
    end
    subgraph P3["Phase 3: 比較候選方案"]
        P3S1["1. Think：提出至少兩<br/>個具實質差異的做法"]
        P3S2["2. Ask：提出候選方案比較"]
        G_P3S2_1{"需要重新定義問題？"}
    end
    subgraph P4["Phase 4: 交付驗收成果"]
        P4S1["1. Think：設計小規模測試"]
        G_P4S1_1{"選定方案可以直接<br/>進入完整實作？"}
        P4S2["2. Write：實作驗證切片"]
        G_P4S2_1{"方案行不通？"}
        P4S3["3. Write：完成選定方<br/>案的完整實作與測試"]
        P4S4["4. Read：執行完整驗證並確認成功準則"]
        P4S5["5. Ask：提出雙鑽石紀錄與成果回報"]
        G_P4S5_1{"實作中發現需求需修正？"}
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| P2S1
    G_P1S3_1 -->|否| P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P2S1
    G_P2S2_1 -->|否| G_P2S2_2
    G_P2S2_2 -->|是| P1S1
    G_P2S2_2 -->|否| P3S1
    P3S1 --> P3S2
    P3S2 --> G_P3S2_1
    G_P3S2_1 -->|是| P2S1
    G_P3S2_1 -->|否| P4S1
    P4S1 --> G_P4S1_1
    G_P4S1_1 -->|是| P4S3
    G_P4S1_1 -->|否| P4S2
    P4S2 --> G_P4S2_1
    G_P4S2_1 -->|是| P3S1
    G_P4S2_1 -->|否| P4S3
    P4S3 --> P4S4
    P4S4 --> P4S5
    P4S5 --> G_P4S5_1
    G_P4S5_1 -->|是| P2S1
    G_P4S5_1 -->|否| End
```
</details>
