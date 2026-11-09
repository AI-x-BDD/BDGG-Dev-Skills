---
name: testplan
description: 跑完 /system-analysis、要在 /tasks 之前替功能規格定好測試計劃時,用這支 Skill 照 plan.md 的端點盤點與規格檔列出待測端點,再以使用者故事為單位、依端點與跨端點驗收寫出 FR 與 NFR 的假如/當/則測試案例,跨故事的 NFR 整理成全域測試區,交出通過需求覆蓋檢查、可交給 /tasks 的 specs/<功能>/testplan.md;使用者提到 testplan、測試計劃、測試計畫、test plan、測試情境、測試案例、test case、NFR 驗證、先規劃測試時使用。(未驗證)
---

# SOP

## Phase 1: 提出待測端點
1. Read **這次規劃的依據**:spec.md、plan.md 的端點盤點與它指到的規格檔與原型、techstack.md、research.md,以及範疇內已經有的程式碼與測試,包含測試裡代替真元件的替身;若 spec.md 所在的資料夾沒有 plan.md → 結束。
2. Think 依 `rules/待測端點-規範.md` **照抄端點盤點列出待測端點**:每個端點的代號、介面規格檔、公開接縫、受測操作與規格錨點、接縫的取捨、替身,以及上游沒寫到的待決問題。
3. Ask 依骨架 `templates/testplan.md` 與範例 `templates/testplan.example.md` **提出待測端點與待決問題**,問使用者是否同意只在這些端點與操作上規劃測試、每一題怎麼決定;若使用者要修改 → 跳至 Phase 1 Step 2。
4. Write 把使用者的決定**登記到 plan.md 的待決問題**。

## Phase 2: 寫出測試計劃
1. Write 依 `rules/測試案例-規範.md` 照確認過的待測端點,把每個使用者故事的端點節、跨端點驗收與全域測試區的測試案例**寫成 `specs/<功能>/testplan.md`**。
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_testplan.py --spec <spec.md 的路徑> --plan <testplan.md 的路徑>` **取得覆蓋檢查的結果**;若有不過 → 跳至 Phase 2 Step 1。
3. Ask **提出測試計劃**與會碰到正式資料或共用服務的實跑案例,問使用者是否同意照它交給 `/tasks`、這些案例可不可以照寫的護欄執行;若使用者要修改 → 跳至 Phase 2 Step 1。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出待測端點"]
        P1S1["1. Read：這次規劃的依據"]
        G_P1S1_1{"spec.md 所在的資料<br/>夾沒有 plan.md？"}
        P1S2["2. Think：照抄端點盤點列出待測端點"]
        P1S3["3. Ask：提出待測端點與待決問題"]
        G_P1S3_1{"使用者要修改？"}
        P1S4["4. Write：登記到 plan.md 的待決問題"]
    end
    subgraph P2["Phase 2: 寫出測試計劃"]
        P2S1["1. Write：寫成 specs/<br/>&lt;功能&gt;/testplan.md"]
        P2S2["2. Delegate：取得覆蓋檢查的結果"]
        G_P2S2_1{"有不過？"}
        P2S3["3. Ask：提出測試計劃"]
        G_P2S3_1{"使用者要修改？"}
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| End
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| P1S2
    G_P1S3_1 -->|否| P1S4
    P1S4 --> P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P2S1
    G_P2S2_1 -->|否| P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P2S1
    G_P2S3_1 -->|否| End
```
</details>
