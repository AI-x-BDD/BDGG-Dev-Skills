---
name: tasks
description: 跑完 /testplan、要依測試計劃與系統分析的產出拆實作任務時,用這支 Skill 照 testplan.md 的使用者故事、端點節與跨端點驗收排出任務,每個行為測試案例一組 /tdd 紅燈與綠燈任務、每節一個 /tdd 重構任務、量測案例一個 📏 量測任務,每個任務以 🧪 指到案例、⚙ 綁到規格檔的錨點、📎 寫出依據,交出通過錨點、介面與案例覆蓋檢查的 tasks.md;使用者提到 tasks、tasks.md、任務清單、拆任務、實作任務、task breakdown、speckit tasks、工作分解時使用。(未驗證)
---

# SOP

## Phase 1: 列出介面元素
1. Read **任務的依據**:spec.md、testplan.md、research.md、techstack.md、plan.md,以及 plan.md Documentation 樹列出的每一個規格檔與原型,以及 spec.md 所在資料夾的 verify-plan.md(有的話);若 testplan.md 不存在 → 結束。
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/list_elements.py --package <spec package 的路徑>` **取得規格檔裡的每一個介面元素**。
3. Delegate 執行 `uv run scripts/constitution_rules.py --constitution <專案根目錄>/constitution --artifact tasks/tasks` **取得套用到 tasks.md 的憲法條文**。

## Phase 2: 寫出 tasks.md
1. Read **這次會改到的既有程式與測試**:plan.md Source Code 樹列出要改或移除的既有檔、前一迭代 tasks.md 的介面覆蓋表,被改掉或移除的符號在既有程式裡的每一個呼叫端,以及新增的列舉值、狀態或類型的既有同類值在既有程式裡的每一處。
2. Think 依 `rules/任務-規範.md` 照 testplan.md 的使用者故事、端點節與跨端點驗收**把測試案例與介面元素排成任務**:每個行為測試案例一組紅燈與綠燈任務,每個有案例的節一個重構任務,每個量測案例一個量測任務。
3. Write 依 `rules/憲法-規範.md`、骨架 `templates/tasks.md` 與範例 `templates/tasks.example.md` 在 spec.md 所在的資料夾**寫出 tasks.md**。
4. Write 在 plan.md 的待決問題**登記排任務時先採用的做法**:「提出的步驟」欄寫 `tasks`、「擋住」欄寫「—」、「決定」欄寫「待決」,每一題附上可選的做法並標出先採用的那一種。
5. Delegate 執行 `uv run scripts/check_tasks.py --tasks <tasks.md 的路徑> --package <spec package 的路徑> --testplan <testplan.md 的路徑>` **取得錨點、介面與案例覆蓋的檢查結果**;若有不過 → 跳至 Phase 2 Step 3。
6. Think **逐條對照憲法的條文**;若有不過 → 跳至 Phase 2 Step 3。

## Phase 3: 確認任務清單
1. Ask **提出任務清單與新登記的待決問題**,問使用者每一題怎麼決定、任務要不要修改。
2. Write 把使用者的決定**寫回 plan.md 與 tasks.md**;若改動了任務 → 跳至 Phase 2 Step 5。
3. Report **交出 tasks.md**,附上憲法的對照結果:路徑、每個 phase 的任務數與每個端點節的任務數,以及下一步跑 `/analyze`。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 列出介面元素"]
        P1S1["1. Read：任務的依據"]
        G_P1S1_1{"testplan.md 不存在？"}
        P1S2["2. Delegate：取得規格<br/>檔裡的每一個介面元素"]
        P1S3["3. Delegate：取得套用<br/>到 tasks.md 的憲法條文"]
    end
    subgraph P2["Phase 2: 寫出 tasks.md"]
        P2S1["1. Read：這次會改到的既有程式與測試"]
        P2S2["2. Think：把測試案例<br/>與介面元素排成任務"]
        P2S3["3. Write：寫出 tasks.md"]
        P2S4["4. Write：登記排任務時先採用的做法"]
        P2S5["5. Delegate：取得錨點、<br/>介面與案例覆蓋的檢查結果"]
        G_P2S5_1{"有不過？"}
        P2S6["6. Think：逐條對照憲法的條文"]
        G_P2S6_1{"有不過？"}
    end
    subgraph P3["Phase 3: 確認任務清單"]
        P3S1["1. Ask：提出任務清單<br/>與新登記的待決問題"]
        P3S2["2. Write：寫回 plan.md 與 tasks.md"]
        G_P3S2_1{"改動了任務？"}
        P3S3["3. Report：交出 tasks.md"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| End
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> P2S4
    P2S4 --> P2S5
    P2S5 --> G_P2S5_1
    G_P2S5_1 -->|是| P2S3
    G_P2S5_1 -->|否| P2S6
    P2S6 --> G_P2S6_1
    G_P2S6_1 -->|是| P2S3
    G_P2S6_1 -->|否| P3S1
    P3S1 --> P3S2
    P3S2 --> G_P3S2_1
    G_P3S2_1 -->|是| P2S5
    G_P3S2_1 -->|否| P3S3
    P3S3 --> End
```
</details>
