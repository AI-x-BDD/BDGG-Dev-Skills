---
name: analyze
description: /tasks 交出 tasks.md 之後、開始實作之前,要交叉檢查 spec package 各產出物彼此是否一致時,用這支 Skill 先跑前置檢查,再讀規格、技術研究、系統分析的規格檔與原型、tasks.md 與憲法,找出跨檔的矛盾、遺漏、無法實作與無法追溯,標出嚴重度與要回哪一支 Skill 修,追加到 analysis.md 並判定能不能進 /implement;使用者提到 analyze、分析、交叉檢查、一致性檢查、實作前檢查、cross-artifact、speckit analyze 時使用。(未驗證)
---

# SOP

## Phase 1: 取得前置檢查結果
1. Read **要分析的 spec package 與前一次迭代**:使用者沒有指定時,用 `specs/` 底下編號最大的資料夾;spec.md 有註明時記下那一次迭代的 plan.md。
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/preflight.py --package <spec package 的路徑>`(spec.md 註明建立在前一次迭代之上時,再加 `--previous-plan <前一次迭代的 plan.md 的路徑>`)**取得前置檢查的結果**;若有不過 → 跳至 Phase 3 Step 3。

## Phase 2: 列出跨檔問題
1. Read **全部產出物與憲法**:spec.md、research.md、techstack.md、plan.md,plan.md Documentation 樹列出的每一個規格檔與原型,tasks.md,`<專案根目錄>/constitution/` 底下的條文,以及既有的 analysis.md。
2. Think 依 `rules/問題-規範.md` **列出跨檔問題、要轉交的模糊與修正順序**:上一輪的問題逐一重判狀態,新問題寫出類別、嚴重度、位置與回哪一步。

## Phase 3: 交出 analysis.md
1. Write 依骨架 `templates/analysis.md` 與範例 `templates/analysis.example.md` 在 spec package **追加這一輪並更新判定**:沒有 analysis.md 時建立,其他產出物一律不改。
2. Delegate 執行 `uv run scripts/check_analysis.py --analysis <analysis.md 的路徑>` **取得 analysis.md 的檢查結果**;若有不過 → 跳至 Phase 3 Step 1。
3. Report **交出判定與下一步**:analysis.md 的路徑、這一輪的問題數、能不能進 `/implement`、要先回哪一支 Skill;前置檢查沒過時,改交出沒過的檢查與要退回的步驟。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 取得前置檢查結果"]
        P1S1["1. Read：要分析的 spec<br/>package 與前一次迭代"]
        P1S2["2. Delegate：取得前置檢查的結果"]
        G_P1S2_1{"有不過？"}
    end
    subgraph P2["Phase 2: 列出跨檔問題"]
        P2S1["1. Read：全部產出物與憲法"]
        P2S2["2. Think：列出跨檔問題、<br/>要轉交的模糊與修正順序"]
    end
    subgraph P3["Phase 3: 交出 analysis.md"]
        P3S1["1. Write：追加這一輪並更新判定"]
        P3S2["2. Delegate：取得<br/>analysis.md 的檢查結果"]
        G_P3S2_1{"有不過？"}
        P3S3["3. Report：交出判定與下一步"]
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> G_P1S2_1
    G_P1S2_1 -->|是| P3S3
    G_P1S2_1 -->|否| P2S1
    P2S1 --> P2S2
    P2S2 --> P3S1
    P3S1 --> P3S2
    P3S2 --> G_P3S2_1
    G_P3S2_1 -->|是| P3S1
    G_P3S2_1 -->|否| P3S3
    P3S3 --> End
```
</details>
