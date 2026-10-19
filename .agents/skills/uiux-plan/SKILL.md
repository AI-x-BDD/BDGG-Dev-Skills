---
name: uiux-plan
description: 要分析前端畫面與互動、想先看到介面長什麼樣子,手上已經有功能規格或 plan.md 指派了前端這一步時,用這支 Skill 從使用者故事盤點畫面與流程,定下審美方向,交出含假資料、點開就能操作的 HTML 原型;使用者提到 UI 設計、UX、畫面設計、wireframe、mockup、原型、prototype、介面長什麼樣子、做個畫面給我看時使用。
---

# SOP

## Phase 1: 盤點畫面
1. Read **這次要分析的介面**:plan.md 的端點盤點與波段表裡指派給這次的那一步;若 plan.md 指派了這一步 → 跳至 Phase 1 Step 3。
2. Ask 問使用者**這次要分析的端點、介面與需求出處**。
3. Read **分析的依據**:spec.md、research.md、techstack.md,以及這一步的理由欄點名的前幾步產出。
4. Think **盤點畫面與互動流程**:每個需求出處都要對到至少一個畫面。

## Phase 2: 做出原型
1. Think 依 `rules/原型-規範.md` **定下審美方向與每個畫面的狀態**。
2. Write 依骨架 `templates/style.css` 與範例 `templates/style.example.css` 在 plan.md 的 Documentation 樹替這一步列的資料夾(沒有 plan.md 時是 spec.md 旁的 `prototype/`)**寫出 `style.css`**。
3. Write 依骨架 `templates/mock.js` 與範例 `templates/mock.example.js` 在同一個資料夾**寫出 `mock.js`**。
4. Write 依骨架 `templates/page.html` 與範例 `templates/page.example.html` 在同一個資料夾**寫出每個畫面的 HTML**:入口是 `index.html`。
5. Write 依骨架 `templates/states.html` 與範例 `templates/states.example.html` 在同一個資料夾**寫出狀態總覽 `states.html`**:每個畫面的每個狀態各一格。
6. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_prototype.py --prototype <prototype 資料夾的路徑> --plan <plan.md 的路徑> --spec <spec.md 的路徑> --step <S 編號>` **取得原型的檢查結果**;若有不過 → 跳至 Phase 2 Step 2。
7. Report **交出原型與待決問題**:附上打開入口 `index.html` 與狀態總覽 `states.html` 的方式,拿不準、要使用者決定的事一起列在這裡。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 盤點畫面"]
        P1S1["1. Read：這次要分析的介面"]
        G_P1S1_1{"plan.md 指派了這一步？"}
        P1S2["2. Ask：這次要分析的<br/>端點、介面與需求出處"]
        P1S3["3. Read：分析的依據"]
        P1S4["4. Think：盤點畫面與互動流程"]
    end
    subgraph P2["Phase 2: 做出原型"]
        P2S1["1. Think：定下審美方<br/>向與每個畫面的狀態"]
        P2S2["2. Write：寫出 style.css"]
        P2S3["3. Write：寫出 mock.js"]
        P2S4["4. Write：寫出每個畫面的 HTML"]
        P2S5["5. Write：寫出狀態總覽 states.html"]
        P2S6["6. Delegate：取得原型的檢查結果"]
        G_P2S6_1{"有不過？"}
        P2S7["7. Report：交出原型與待決問題"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| P1S3
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> P1S4
    P1S4 --> P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> P2S4
    P2S4 --> P2S5
    P2S5 --> P2S6
    P2S6 --> G_P2S6_1
    G_P2S6_1 -->|是| P2S2
    G_P2S6_1 -->|否| P2S7
    P2S7 --> End
```
</details>
