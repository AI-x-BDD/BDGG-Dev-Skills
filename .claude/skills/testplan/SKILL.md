---
name: testplan
description: 跑完 /system-analysis、要在 /tasks 之前替功能規格定好測試計劃時,用這支 Skill 照 plan.md 的端點盤點與規格檔列出待測端點,再以使用者故事為單位、依端點與跨端點驗收寫出 FR 與 NFR 的假如/當/則測試案例,跨故事的 NFR 整理成全域測試區,交出通過需求覆蓋檢查、可交給 /tasks 的 specs/<功能>/testplan.md;使用者提到 testplan、測試計劃、測試計畫、test plan、測試情境、測試案例、test case、NFR 驗證、先規劃測試時使用。(未驗證)
---

# SOP

## Phase 1: 提出待測端點
1. Read **這次規劃的依據**:spec.md、plan.md 的端點盤點與它指到的規格檔與原型、techstack.md、research.md,以及範疇內已經有的程式碼與測試,包含測試裡代替真元件的替身;若 spec.md 所在的資料夾沒有 plan.md → 結束;若要補的是已經交出的 testplan.md 的案例 → 跳至 Phase 2 Step 1。
2. Think 依 `rules/待測端點-規範.md` **照抄端點盤點列出待測端點**:每個端點的代號、介面規格檔、公開接縫、受測操作與規格錨點、接縫的取捨、替身,以及上游沒寫到的待決問題。
3. Ask 依骨架 `templates/testplan.md` 與範例 `templates/testplan.example.md` **提出待測端點與待決問題**,問使用者是否同意只在這些端點與操作上規劃測試、每一題怎麼決定;若使用者要修改 → 跳至 Phase 1 Step 2。
4. Write 把使用者的決定**登記到 plan.md 的待決問題**。

## Phase 2: 寫出測試計劃
1. Delegate 依骨架 `templates/端點節指示.md` 與範例 `templates/端點節指示.example.md` 把每個要寫或要補的端點節交給 subagent **平行寫成端點節的案例**。
2. Write 依 `rules/測試案例-規範.md` 把交回的端點節、跨端點驗收與全域測試區的測試案例**寫成 `specs/<功能>/testplan.md`**:端點節照交回的原文。
3. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_testplan.py --spec <spec.md 的路徑> --plan <testplan.md 的路徑> --contracts <spec package 的 contracts 資料夾>` **取得覆蓋檢查的結果**;若端點節的案例有不過 → 跳至 Phase 2 Step 1;若其他有不過 → 跳至 Phase 2 Step 2。
4. Ask **提出測試計劃**與會碰到正式資料或共用服務的實跑案例,問使用者是否同意照它交給 `/tasks`、這些案例可不可以照寫的護欄執行;若使用者要修改 → 跳至 Phase 2 Step 1。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出待測端點"]
        P1S1["1. Read：這次規劃的依據"]
        G_P1S1_1{"spec.md 所在的資料<br/>夾沒有 plan.md？"}
        G_P1S1_2{"要補的是已經交出的<br/>testplan.md 的案例？"}
        P1S2["2. Think：照抄端點盤點列出待測端點"]
        P1S3["3. Ask：提出待測端點與待決問題"]
        G_P1S3_1{"使用者要修改？"}
        P1S4["4. Write：登記到 plan.md 的待決問題"]
    end
    subgraph P2["Phase 2: 寫出測試計劃"]
        P2S1["1. Delegate：平行寫成端點節的案例"]
        P2S2["2. Write：寫成 specs/<br/>&lt;功能&gt;/testplan.md"]
        P2S3["3. Delegate：取得覆蓋檢查的結果"]
        G_P2S3_1{"端點節的案例有不過？"}
        G_P2S3_2{"其他有不過？"}
        P2S4["4. Ask：提出測試計劃"]
        G_P2S4_1{"使用者要修改？"}
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| End
    G_P1S1_1 -->|否| G_P1S1_2
    G_P1S1_2 -->|是| P2S1
    G_P1S1_2 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| P1S2
    G_P1S3_1 -->|否| P1S4
    P1S4 --> P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P2S1
    G_P2S3_1 -->|否| G_P2S3_2
    G_P2S3_2 -->|是| P2S2
    G_P2S3_2 -->|否| P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P2S1
    G_P2S4_1 -->|否| End
```
</details>
