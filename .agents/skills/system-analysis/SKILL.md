---
name: system-analysis
description: 要依功能規格與技術研究規劃系統分析、還沒開始分析各端點的介面之前,用這支 Skill 從需求盤點涉及的技術端點(前端、後端、資料庫、第三方、硬體、手機、雲端)與各自對外的介面,依相依關係排成可以平行分析的 wave,交出只含規劃、通過結構檢查的 plan.md;使用者提到系統分析、system analysis、分析規劃、端點盤點、介面分析、wave、波段、平行分析、plan.md 時使用。(未驗證)
---

# SOP

## Phase 1: 盤點端點
1. Read **規劃的依據**:spec.md、research.md 與 techstack.md。
2. Think 依 `rules/端點-規範.md` **盤點這次需求涉及的端點**:每個端點視為一個獨立系統,寫出它對外的介面與需求出處。
3. Ask **提出端點盤點**,問使用者是否要增減;若使用者要修改 → 跳至 Phase 1 Step 2。

## Phase 2: 寫出 plan.md
1. Think 依 `rules/波段-規範.md` **排出分析波段**:每個介面至少占一個步驟,同一波的介面彼此不依賴。
2. Write 依骨架 `templates/plan.md` 與範例 `templates/plan.example.md` 在 spec.md 所在的資料夾**寫出 plan.md**。
3. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_plan.py --plan <plan.md 的路徑> --spec <spec.md 的路徑>` **取得 plan.md 的結構檢查結果**;若有不過 → 跳至 Phase 2 Step 2。
4. Ask **提出分析波段**,問使用者是否同意;若使用者要修改 → 跳至 Phase 2 Step 1。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 盤點端點"]
        P1S1["1. Read：規劃的依據"]
        P1S2["2. Think：盤點這次需求涉及的端點"]
        P1S3["3. Ask：提出端點盤點"]
        G_P1S3_1{"使用者要修改？"}
    end
    subgraph P2["Phase 2: 寫出 plan.md"]
        P2S1["1. Think：排出分析波段"]
        P2S2["2. Write：寫出 plan.md"]
        P2S3["3. Delegate：取得<br/>plan.md 的結構檢查結果"]
        G_P2S3_1{"有不過？"}
        P2S4["4. Ask：提出分析波段"]
        G_P2S4_1{"使用者要修改？"}
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| P1S2
    G_P1S3_1 -->|否| P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P2S2
    G_P2S3_1 -->|否| P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P2S1
    G_P2S4_1 -->|否| End
```
</details>
