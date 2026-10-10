---
name: skill-form-sop
description: 撰寫或修改 Skill 的 SKILL.md 中 SOP 流程（Phase、步驟與按需載入步驟）時，必須使用此 Skill；使用者提到 SOP、流程、Phase、workflow steps 時使用。使用者因既有 Skill 的產出不符預期而要求修改時，先用 skill-engineering 分析根因，即使已指定步驟或修法亦同；依已確認方案轉交本 Skill 執行時，直接承接。(未驗證)
---

# SOP

## Phase 1: 寫出 SOP
1. Read **目標 skill 已有的 SKILL.md**。
2. Write 依 `rules/SOP-格式規範.md` 把使用者要的流程**寫成目標 skill 的 `# SOP`**。
3. Write 依 `rules/SOP-按需載入-格式規範.md` **替用得到的步驟寫上指標**。
4. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/render_sop_diagram.py --write --file <目標 SKILL.md 的路徑>` **取得格式檢查的結果**並產生流程視覺圖注入目標 skill 的 `SKILL.md` 檔尾;若檢查有不過 → 跳至 Phase 1 Step 2。

## Phase 2: 列出把關紀錄
1. Read **剛寫進目標 skill 的 `# SOP`**。
2. Think 依 `rules/把關紀錄-格式規範.md` **列出把關紀錄**;若有 must 不過 → 跳至 Phase 1 Step 2。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 寫出 SOP"]
        P1S1["1. Read：目標 skill 已有的 SKILL.md"]
        P1S2["2. Write：寫成目標 skill 的 # SOP"]
        P1S3["3. Write：替用得到的步驟寫上指標"]
        P1S4["4. Delegate：取得格式檢查的結果"]
        G_P1S4_1{"檢查有不過？"}
    end
    subgraph P2["Phase 2: 列出把關紀錄"]
        P2S1["1. Read：剛寫進目標 skill 的 # SOP"]
        P2S2["2. Think：列出把關紀錄"]
        G_P2S2_1{"有 must 不過？"}
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> P1S4
    P1S4 --> G_P1S4_1
    G_P1S4_1 -->|是| P1S2
    G_P1S4_1 -->|否| P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P1S2
    G_P2S2_1 -->|否| End
```
</details>
