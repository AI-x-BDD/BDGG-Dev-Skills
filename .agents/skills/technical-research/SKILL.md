---
name: technical-research
description: 要依功能規格開始規劃實作、需要先研究技術選型與未知數時,用這支 Skill 依 spec.md 與使用者指定的技術方向列出研究項,逐項以實測、估算、查證或判斷取得證據並做出決策,交出通過結構檢查的 research.md 與總結技術堆疊的 techstack.md;使用者提到技術研究、技術選型、技術堆疊、tech stack、research.md、Phase 0、spike、可行性評估、先研究再規劃時使用。(未驗證)
---

# SOP

## Phase 1: 列出研究項
1. Read **研究的依據**:spec.md 與使用者指定的技術方向。
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/constitution_rules.py --constitution <專案根目錄>/constitution --artifact technical-research/research --artifact technical-research/techstack` **取得套用到研究產出的憲法條文**。
3. Think 依 `rules/研究項-規範.md` **列出研究項**:每個會影響實作的技術未知數或選型,標出它對應的 FR、NFR、SC、憲法條文或使用者指定。
4. Ask **提出研究項清單**,問使用者是否要增減;若使用者要修改 → 跳至 Phase 1 Step 3。

## Phase 2: 寫出 research.md 與 techstack.md
1. Read 依 `rules/證據-規範.md` **逐項取得證據**:能實測的在 session 暫存區寫探針實測,不能實測的估算或查證來源,記下環境、依據或來源;若使用者沒有改需求,證據也沒有推翻 spec.md 的需求 → 跳至 Phase 2 Step 3。
2. Delegate 轉交 specify **把改變的需求改進 spec.md**。
3. Think 依 `rules/憲法-規範.md` **決定每個研究項的方案**,以及考慮過但否決的替代方案與原因;若方案依賴 Phase 2 Step 1 沒有取得證據的技術事實(SDK 或函式庫呼叫的行為、既有程式碼做了什麼) → 跳至 Phase 2 Step 1。
4. Write 依骨架 `templates/research.template.md` 與範例 `templates/research.template.example.md` 在 spec.md 所在的資料夾**寫出 research.md**。
5. Write 依骨架 `templates/techstack.template.md` 與範例 `templates/techstack.template.example.md` 在 research.md 所在的資料夾**寫出 techstack.md**。

## Phase 3: 驗收 research.md 與 techstack.md
1. Delegate 執行 `uv run scripts/check_research.py --research <research.md 的路徑>` **取得 research.md 的結構檢查結果**;若有不過 → 跳至 Phase 2 Step 4。
2. Delegate 執行 `uv run scripts/check_techstack.py --techstack <techstack.md 的路徑>` **取得 techstack.md 的結構檢查結果**;若有不過 → 跳至 Phase 2 Step 5。
3. Think **逐條對照憲法的條文**;若有不過 → 跳至 Phase 2 Step 4。
4. Ask **提出研究摘要**,附上憲法的對照結果,問使用者是否同意;若使用者要修改 → 跳至 Phase 2 Step 3。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 列出研究項"]
        P1S1["1. Read：研究的依據"]
        P1S2["2. Delegate：取得套用<br/>到研究產出的憲法條文"]
        P1S3["3. Think：列出研究項"]
        P1S4["4. Ask：提出研究項清單"]
        G_P1S4_1{"使用者要修改？"}
    end
    subgraph P2["Phase 2: 寫出 research.md 與 techstack.md"]
        P2S1["1. Read：逐項取得證據"]
        G_P2S1_1{"使用者沒有改需求,<br/>證據也沒有推翻<br/>spec.md 的需求？"}
        P2S2["2. Delegate：把改變<br/>的需求改進 spec.md"]
        P2S3["3. Think：決定每個研究項的方案"]
        G_P2S3_1{"方案依賴 Phase 2 Step 1<br/>沒有取得證據的技術事實<br/>(SDK 或函式庫呼叫的行為、<br/>既有程式碼做了什麼)？"}
        P2S4["4. Write：寫出 research.md"]
        P2S5["5. Write：寫出 techstack.md"]
    end
    subgraph P3["Phase 3: 驗收 research.md 與 techstack.md"]
        P3S1["1. Delegate：取得<br/>research.md 的結構檢查結果"]
        G_P3S1_1{"有不過？"}
        P3S2["2. Delegate：取得<br/>techstack.md 的結構檢查結果"]
        G_P3S2_1{"有不過？"}
        P3S3["3. Think：逐條對照憲法的條文"]
        G_P3S3_1{"有不過？"}
        P3S4["4. Ask：提出研究摘要"]
        G_P3S4_1{"使用者要修改？"}
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> P1S4
    P1S4 --> G_P1S4_1
    G_P1S4_1 -->|是| P1S3
    G_P1S4_1 -->|否| P2S1
    P2S1 --> G_P2S1_1
    G_P2S1_1 -->|是| P2S3
    G_P2S1_1 -->|否| P2S2
    P2S2 --> P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P2S1
    G_P2S3_1 -->|否| P2S4
    P2S4 --> P2S5
    P2S5 --> P3S1
    P3S1 --> G_P3S1_1
    G_P3S1_1 -->|是| P2S4
    G_P3S1_1 -->|否| P3S2
    P3S2 --> G_P3S2_1
    G_P3S2_1 -->|是| P2S5
    G_P3S2_1 -->|否| P3S3
    P3S3 --> G_P3S3_1
    G_P3S3_1 -->|是| P2S4
    G_P3S3_1 -->|否| P3S4
    P3S4 --> G_P3S4_1
    G_P3S4_1 -->|是| P2S3
    G_P3S4_1 -->|否| End
```

```mermaid
sequenceDiagram
    actor User
    participant Main as technical-research
    participant Sub_1 as specify 把改變的需求改進 spec.md
    Note over User,Sub_1: Phase 1: 列出研究項
    Main->>User: 4. Ask：提出研究項清單
    User-->>Main: 回覆確認
    Note over User,Sub_1: Phase 2: 寫出 research.md 與 techstack.md
    Main->>Sub_1: 2. Delegate：把改變的需求改進 spec.md
    Sub_1-->>Main: 完成並交回產出
    Note over User,Sub_1: Phase 3: 驗收 research.md 與 techstack.md
    Main->>User: 4. Ask：提出研究摘要
    User-->>Main: 回覆確認
```
</details>
