---
name: skill-form-script
description: 當要撰寫 Skill 時,只要涉及腳本的部分(`scripts/` 底下 Python 腳本的撰寫),就必須使用此 Skill。使用者因既有 Skill 的產出不符預期而要求修改時,先用 skill-engineering 分析根因,即使已指定步驟或修法亦同;依已確認方案轉交本 Skill 執行時,直接承接。(未驗證)
---

# SOP

## Phase 1: 補上腳本執行規範
1. Read **目標 skill 現有的內容**:SKILL.md、`rules/` 與 `scripts/` 底下已有的檔;若目標 skill 已有 `rules/腳本執行-規範.md` → 跳至 Phase 2 Step 1。
2. Write 依 `rules/腳本執行規範-格式規範.md` 在目標 skill 的 `rules/` **補上 `腳本執行-規範.md`**。

## Phase 2: 寫出腳本
1. Write 依 `rules/腳本-格式規範.md` 把使用者要的處理寫成目標 skill **`scripts/` 底下的 Python 腳本**。
2. Read 這支腳本以 `uv run` 執行 **`--help` 與一筆實際輸入的輸出**;若與使用者要的結果不符 → 跳至 Phase 2 Step 1。
3. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_scripts.py --skill <目標 skill 的根目錄>` **取得結構檢查的結果**;若〈腳本執行規範照固定內容寫〉不過 → 跳至 Phase 1 Step 2;若其他 Rule 有不過 → 跳至 Phase 2 Step 1。
4. Think **逐條對照腳本沒有判的 Rule**;若有不過 → 跳至 Phase 2 Step 1。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 補上腳本執行規範"]
        P1S1["1. Read：目標 skill 現有的內容"]
        G_P1S1_1{"目標 skill 已有 rules/<br/>腳本執行-規範.md？"}
        P1S2["2. Write：補上 腳本執行-規範.md"]
    end
    subgraph P2["Phase 2: 寫出腳本"]
        P2S1["1. Write：scripts/<br/>底下的 Python 腳本"]
        P2S2["2. Read：--help 與一筆實際輸入的輸出"]
        G_P2S2_1{"與使用者要的結果不符？"}
        P2S3["3. Delegate：取得結構檢查的結果"]
        G_P2S3_1{"〈腳本執行規範照固<br/>定內容寫〉不過？"}
        G_P2S3_2{"其他 Rule 有不過？"}
        P2S4["4. Think：逐條對照腳本沒有判的 Rule"]
        G_P2S4_1{"有不過？"}
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| P2S1
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P2S1
    G_P2S2_1 -->|否| P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P1S2
    G_P2S3_1 -->|否| G_P2S3_2
    G_P2S3_2 -->|是| P2S1
    G_P2S3_2 -->|否| P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P2S1
    G_P2S4_1 -->|否| End
```
</details>
