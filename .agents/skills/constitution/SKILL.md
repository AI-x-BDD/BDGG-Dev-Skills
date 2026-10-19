---
name: constitution
description: 要替專案寫下或修改憲法、想約束 SDD 流程某個產出物(spec.md、OpenAPI、DBML、compose.yaml…)該長什麼樣子時,用這支 Skill 訪談使用者,只就這次需要的產出物寫出加嚴的條文,交出通過結構檢查的 `constitution/` 檔;使用者提到憲法、constitution、專案規範、產出物規範、API 風格、命名慣例、speckit constitution 時使用。(未驗證)
---

# SOP

## Phase 1: 提出條文清單
1. Read **寫條文的依據**:使用者想約束的事、專案現有的 `constitution/`,以及這些事涉及的 SDD Skill 的規範與樣板。
2. Think 依 `rules/條文-規範.md` **把想約束的事拆成條文**:每條歸到一個產出物或 `_shared/`,並對照 Skill 規範與現有條文;若每條都寫得具體 → 跳至 Phase 1 Step 4。
3. Delegate 轉交 clarify **問清楚會改變條文的缺口**。
4. Ask **提出條文清單**:每條的檔、標題、強度與它加嚴的地方,以及不寫成條文的事與原因,問使用者是否同意;若使用者要修改 → 跳至 Phase 1 Step 2;若條文清單是空的 → 跳至 Phase 2 Step 3。

## Phase 2: 寫出憲法檔
1. Write 依骨架 `templates/條文.md` 與範例 `templates/條文.example.md` **把同意的條文寫進對應的憲法檔**:新增的條文接在檔尾,修改的條文改寫原處。
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_constitution.py --constitution <constitution 資料夾的路徑>` **取得憲法檔的結構檢查結果**;若有不過 → 跳至 Phase 2 Step 1。
3. Report **交出改到的檔與每條約束的產出物**。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提出條文清單"]
        P1S1["1. Read：寫條文的依據"]
        P1S2["2. Think：把想約束的事拆成條文"]
        G_P1S2_1{"每條都寫得具體？"}
        P1S3["3. Delegate：問清楚會改變條文的缺口"]
        P1S4["4. Ask：提出條文清單"]
        G_P1S4_1{"使用者要修改？"}
        G_P1S4_2{"條文清單是空的？"}
    end
    subgraph P2["Phase 2: 寫出憲法檔"]
        P2S1["1. Write：把同意的條<br/>文寫進對應的憲法檔"]
        P2S2["2. Delegate：取得憲<br/>法檔的結構檢查結果"]
        G_P2S2_1{"有不過？"}
        P2S3["3. Report：交出改到的<br/>檔與每條約束的產出物"]
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> G_P1S2_1
    G_P1S2_1 -->|是| P1S4
    G_P1S2_1 -->|否| P1S3
    P1S3 --> P1S4
    P1S4 --> G_P1S4_1
    G_P1S4_1 -->|是| P1S2
    G_P1S4_1 -->|否| G_P1S4_2
    G_P1S4_2 -->|是| P2S3
    G_P1S4_2 -->|否| P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P2S1
    G_P2S2_1 -->|否| P2S3
    P2S3 --> End
```

```mermaid
sequenceDiagram
    actor User
    participant Main as constitution
    participant Sub_1 as clarify 問清楚會改變條文的缺口
    Note over User,Sub_1: Phase 1: 提出條文清單
    Main->>Sub_1: 3. Delegate：問清楚會改變條文的缺口
    Sub_1-->>Main: 完成並交回產出
    Main->>User: 4. Ask：提出條文清單
    User-->>Main: 回覆確認
    Note over User,Sub_1: Phase 2: 寫出憲法檔
    Main->>User: 3. Report：交出改到的檔與每條約束的產出物
```
</details>
