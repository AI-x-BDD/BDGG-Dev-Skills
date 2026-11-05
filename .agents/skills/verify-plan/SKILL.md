---
name: verify-plan
description: 系統分析交出規格檔之後、拆任務之前,要規劃怎麼在真實環境驗收時,用這支 Skill 逐條 SC 與使用者故事列出真實元件、自動測試用的替身、實跑做法、樣本、副作用護欄與判定者,交出通過覆蓋檢查、tasks 會讀的 verify-plan.md;使用者提到真實環境驗收、驗收規劃、實測計畫、假工具、測試替身、verify plan 時使用。(未驗證)
---

# SOP

## Phase 1: 寫出 verify-plan.md
1. Read **驗收的依據**:spec.md、research.md、plan.md 與它列出的規格檔。
2. Read **自動測試現有的替身**:專案測試裡假的外部工具、前端函式庫與服務。
3. Think 依 `rules/驗收-規範.md` 逐條 SC 與使用者故事**決定實跑的驗收做法**。
4. Write 依骨架 `templates/verify-plan.md` 與範例 `templates/verify-plan.example.md` 在 spec.md 所在的資料夾**寫出 verify-plan.md**。
5. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_verify_plan.py --verify-plan <verify-plan.md 的路徑> --spec <spec.md 的路徑>` **取得 SC 與故事的覆蓋檢查結果**;若有不過 → 跳至 Phase 1 Step 4。

## Phase 2: 交出 verify-plan.md
1. Ask **提出會碰到正式資料或共用服務的項目**,問使用者是否同意;若使用者要修改 → 跳至 Phase 1 Step 3。
2. Report **交出 verify-plan.md 的路徑**與下一步跑 tasks。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 寫出 verify-plan.md"]
        P1S1["1. Read：驗收的依據"]
        P1S2["2. Read：自動測試現有的替身"]
        P1S3["3. Think：決定實跑的驗收做法"]
        P1S4["4. Write：寫出 verify-plan.md"]
        P1S5["5. Delegate：取得 SC<br/>與故事的覆蓋檢查結果"]
        G_P1S5_1{"有不過？"}
    end
    subgraph P2["Phase 2: 交出 verify-plan.md"]
        P2S1["1. Ask：提出會碰到正式<br/>資料或共用服務的項目"]
        G_P2S1_1{"使用者要修改？"}
        P2S2["2. Report：交出<br/>verify-plan.md 的路徑"]
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> P1S4
    P1S4 --> P1S5
    P1S5 --> G_P1S5_1
    G_P1S5_1 -->|是| P1S4
    G_P1S5_1 -->|否| P2S1
    P2S1 --> G_P2S1_1
    G_P2S1_1 -->|是| P1S3
    G_P2S1_1 -->|否| P2S2
    P2S2 --> End
```
</details>
