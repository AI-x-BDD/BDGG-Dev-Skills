---
name: clarify
description: 需求有缺漏、矛盾、模糊或還沒拍板的決策、不該由 AI 自己補完時,用這支 Skill 盤點影響最大的缺口,在對話裡一輪問 1 到 3 題、每題附 Context 與標出推薦的選項表,交還使用者拍板的決策、補充與剩餘風險;別支 Skill 要先釐清需求時也轉交這支;使用者提到 clarify、釐清需求、訪談我、問我問題、需求不清楚、有歧義、先問清楚、interview 時使用。(未驗證)
---

# SOP

## Phase 1: 列出需求缺口
1. Read **使用者的需求與呼叫者的指示**:要澄清的主題、指定的提問面向、要不要記錄問答。
2. Think 依 `rules/提問-規範.md` **列出需求的缺口**:缺漏、矛盾、模糊與未拍板的決策。

## Phase 2: 取得使用者的回答
1. Ask 依 `rules/Context與選項-規範.md`、骨架 `templates/提問.md` 與範例 `templates/提問.example.md` 在對話裡**提出本輪 1 到 3 題**,不用提問工具,請使用者依題號回答選項編號。
2. Think 依 `rules/決策-規範.md` **整理已拍板的決策與仍未解決的缺口**;若使用者表示要停 → 跳至 Phase 3 Step 1;若有回答對不上選項 → 跳至 Phase 2 Step 1;若還有會改變結果的缺口且累計未滿 5 題 → 跳至 Phase 1 Step 2。

## Phase 3: 交還澄清結果
1. Report 依骨架 `templates/澄清結果.md` 與範例 `templates/澄清結果.example.md` **交還澄清結果**:已確認的決策、使用者的補充與剩餘的風險;若呼叫者只要在對話裡交還 → 結束。
2. Write **把澄清結果寫進呼叫者指定的檔**。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 列出需求缺口"]
        P1S1["1. Read：使用者的需求與呼叫者的指示"]
        P1S2["2. Think：列出需求的缺口"]
    end
    subgraph P2["Phase 2: 取得使用者的回答"]
        P2S1["1. Ask：提出本輪 1 到 3 題"]
        P2S2["2. Think：整理已拍板的<br/>決策與仍未解決的缺口"]
        G_P2S2_1{"使用者表示要停？"}
        G_P2S2_2{"有回答對不上選項？"}
        G_P2S2_3{"還有會改變結果的缺<br/>口且累計未滿 5 題？"}
    end
    subgraph P3["Phase 3: 交還澄清結果"]
        P3S1["1. Report：交還澄清結果"]
        G_P3S1_1{"呼叫者只要在對話裡交還？"}
        P3S2["2. Write：把澄清結果<br/>寫進呼叫者指定的檔"]
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P3S1
    G_P2S2_1 -->|否| G_P2S2_2
    G_P2S2_2 -->|是| P2S1
    G_P2S2_2 -->|否| G_P2S2_3
    G_P2S2_3 -->|是| P1S2
    G_P2S2_3 -->|否| P3S1
    P3S1 --> G_P3S1_1
    G_P3S1_1 -->|是| End
    G_P3S1_1 -->|否| P3S2
    P3S2 --> End
```
</details>
