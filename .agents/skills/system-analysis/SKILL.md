---
name: system-analysis
description: 要依功能規格與技術研究規劃並執行系統分析時,用這支 Skill 盤點涉及的技術端點(前端、後端、資料庫、第三方、硬體、手機、雲端)與各自對外的介面,排成可以平行分析的 wave,替每一步指派 ui-plan、data-plan、api-plan 或 deploy-plan,再一波一波交給 sub agent 執行,交出 plan.md 與各介面可以直接交付的規格檔和原型;使用者提到系統分析、system analysis、分析規劃、端點盤點、介面分析、wave、波段、平行分析、plan.md 時使用。(未驗證)
---

# SOP

## Phase 1: 盤點端點
1. Read **規劃的依據**:spec.md、research.md 與 techstack.md。
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/constitution_rules.py --constitution <專案根目錄>/constitution --artifact system-analysis/plan` **取得套用到 plan.md 的憲法條文**。
3. Think 依 `rules/端點-規範.md` **盤點這次需求涉及的端點**:每個端點視為一個獨立系統,寫出它對外的介面與需求出處。
4. Ask **提出端點盤點**,問使用者是否要增減;若使用者要修改 → 跳至 Phase 1 Step 3。

## Phase 2: 寫出 plan.md
1. Think 依 `rules/波段-規範.md` **排出分析波段並指派 planner**:每個介面至少占一個步驟,同一波的介面彼此不依賴。
2. Write 依 `rules/憲法-規範.md`、骨架 `templates/plan.md` 與範例 `templates/plan.example.md` 在 spec.md 所在的資料夾**寫出 plan.md**。
3. Delegate 執行 `uv run scripts/check_plan.py --plan <plan.md 的路徑> --spec <spec.md 的路徑>` **取得 plan.md 的結構檢查結果**;若有不過 → 跳至 Phase 2 Step 2。
4. Think **逐條對照憲法的條文**;若有不過 → 跳至 Phase 2 Step 2。
5. Ask **提出分析波段與指派的 planner**,附上憲法的對照結果,問使用者是否同意;若使用者要修改 → 跳至 Phase 2 Step 1。

## Phase 3: 執行分析波段
1. Delegate 依骨架 `templates/委派指示.md` 與範例 `templates/委派指示.example.md` **把這一輪的步驟交給 sub agent**:還沒完成的最前面一波或使用者要重做的步驟,一支 planner 一個 sub agent,同一波平行。
2. Read **這一輪交回的產出與待決問題**。
3. Write 依 `rules/待決問題-規範.md` 在 plan.md **登記待決問題**:每一題標出它擋住哪幾步。
4. Delegate 執行 `uv run scripts/check_plan.py --plan <plan.md 的路徑> --spec <spec.md 的路徑>` **取得規格檔引用與待決問題表的檢查結果**;若有不過 → 跳至 Phase 3 Step 3;若有問題擋住下一波 → 跳至 Phase 3 Step 5;若還有下一波 → 跳至 Phase 3 Step 1。
5. Ask **提出還沒決定的待決問題**,問使用者每一題怎麼決定。
6. Write **把使用者的決定寫回 plan.md**;若決定要改已經完成的產出,或還有下一波 → 跳至 Phase 3 Step 1。
7. Report **交出所有產出**:每個檔的路徑,以及打開原型的方式。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 盤點端點"]
        P1S1["1. Read：規劃的依據"]
        P1S2["2. Delegate：取得套用<br/>到 plan.md 的憲法條文"]
        P1S3["3. Think：盤點這次需求涉及的端點"]
        P1S4["4. Ask：提出端點盤點"]
        G_P1S4_1{"使用者要修改？"}
    end
    subgraph P2["Phase 2: 寫出 plan.md"]
        P2S1["1. Think：排出分析波段並指派 planner"]
        P2S2["2. Write：寫出 plan.md"]
        P2S3["3. Delegate：取得<br/>plan.md 的結構檢查結果"]
        G_P2S3_1{"有不過？"}
        P2S4["4. Think：逐條對照憲法的條文"]
        G_P2S4_1{"有不過？"}
        P2S5["5. Ask：提出分析波段與指派的 planner"]
        G_P2S5_1{"使用者要修改？"}
    end
    subgraph P3["Phase 3: 執行分析波段"]
        P3S1["1. Delegate：把這一輪<br/>的步驟交給 sub agent"]
        P3S2["2. Read：這一輪交回的產出與待決問題"]
        P3S3["3. Write：登記待決問題"]
        P3S4["4. Delegate：取得規格檔引<br/>用與待決問題表的檢查結果"]
        G_P3S4_1{"有不過？"}
        G_P3S4_2{"有問題擋住下一波？"}
        G_P3S4_3{"還有下一波？"}
        P3S5["5. Ask：提出還沒決定的待決問題"]
        P3S6["6. Write：把使用者的決定寫回 plan.md"]
        G_P3S6_1{"決定要改已經完成的<br/>產出,或還有下一波？"}
        P3S7["7. Report：交出所有產出"]
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> P1S4
    P1S4 --> G_P1S4_1
    G_P1S4_1 -->|是| P1S3
    G_P1S4_1 -->|否| P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P2S2
    G_P2S3_1 -->|否| P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P2S2
    G_P2S4_1 -->|否| P2S5
    P2S5 --> G_P2S5_1
    G_P2S5_1 -->|是| P2S1
    G_P2S5_1 -->|否| P3S1
    P3S1 --> P3S2
    P3S2 --> P3S3
    P3S3 --> P3S4
    P3S4 --> G_P3S4_1
    G_P3S4_1 -->|是| P3S3
    G_P3S4_1 -->|否| G_P3S4_2
    G_P3S4_2 -->|是| P3S5
    G_P3S4_2 -->|否| G_P3S4_3
    G_P3S4_3 -->|是| P3S1
    G_P3S4_3 -->|否| P3S5
    P3S5 --> P3S6
    P3S6 --> G_P3S6_1
    G_P3S6_1 -->|是| P3S1
    G_P3S6_1 -->|否| P3S7
    P3S7 --> End
```
</details>
