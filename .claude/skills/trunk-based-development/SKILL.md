---
name: trunk-based-development
description: 開始做一個功能、要切分支或決定分支策略、要合併或推送到 remote、修復 production bug 或處理多日變更時,用這支 Skill 依主幹式開發(Trunk-Based Development)規範切分、驗證並整合程式碼;使用者提到主幹開發、trunk-based development、TBD、開 branch、開 PR、merge、push、切分支、長期分支、feature flag、branch by abstraction 時使用。(未驗證)
---

# SOP

## Phase 1: 同步開工環境
1. Read **目前 repo 的開工狀態**:remote 狀態、預設 branch、工作目錄是否有未提交變更,以及 CI 與本機建置指令。
2. Think 依 `rules/開工判斷-規範.md` **評估變更規模與選擇整合風格**(直接進 trunk 或短期 branch)。
3. Write **同步 trunk 的最新狀態**;若整合風格是直接進 trunk → 跳至 Phase 2 Step 1。
4. Write **由最新 trunk 開出短期 branch**。

## Phase 2: 完成通過本機建置的變更
1. Write 依 `rules/分支與變更-規範.md` **實作功能或修復並編寫測試**,在本機形成 commit;長變更使用 feature flag 或 branch by abstraction 隔絕未完成功能。
2. Write 以 `--autostash` **從 trunk 拉取最新變更**並帶入本機,並在本機解決衝突。
3. Read 在本機執行完整建置指令的**編譯與所有測試的結果**;若建置或測試失敗 → 跳至 Phase 2 Step 1。

## Phase 3: 把變更整合進 trunk
1. Write **將變更推送到 remote**;若整合風格是直接進 trunk → 跳至 Phase 3 Step 3。
2. Write 發起 PR,**通過 review 與 CI 後合併回 trunk**,並立刻刪除短期 branch。
3. Read 確認 remote trunk 上**最新 commit 的建置或 CI 狀態**;若狀態為綠 → 跳至 Phase 4 Step 1。
4. Write **revert remote trunk 上這次的 commit**,照這次的整合風格送上 remote。
5. Read remote 上 **revert 後 trunk 的建置或 CI 狀態**;若狀態為綠 → 跳至 Phase 1 Step 3。

## Phase 4: 交付整合回報
1. Report 依骨架 `templates/整合回報.md` 與範例 `templates/整合回報.example.md` **向使用者回報整合結果**,列出切法、整合風格、本機建置證據、trunk 狀態與留下的開關或技術債。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 同步開工環境"]
        P1S1["1. Read：目前 repo 的開工狀態"]
        P1S2["2. Think：評估變更規模與選擇整合風格"]
        P1S3["3. Write：同步 trunk 的最新狀態"]
        G_P1S3_1{"整合風格是直接進 trunk？"}
        P1S4["4. Write：由最新<br/>trunk 開出短期 branch"]
    end
    subgraph P2["Phase 2: 完成通過本機建置的變更"]
        P2S1["1. Write：實作功能或修復並編寫測試"]
        P2S2["2. Write：從 trunk 拉取最新變更"]
        P2S3["3. Read：編譯與所有測試的結果"]
        G_P2S3_1{"建置或測試失敗？"}
    end
    subgraph P3["Phase 3: 把變更整合進 trunk"]
        P3S1["1. Write：將變更推送到 remote"]
        G_P3S1_1{"整合風格是直接進 trunk？"}
        P3S2["2. Write：通過 review<br/>與 CI 後合併回 trunk"]
        P3S3["3. Read：最新 commit<br/>的建置或 CI 狀態"]
        G_P3S3_1{"狀態為綠？"}
        P3S4["4. Write：revert remote<br/>trunk 上這次的 commit"]
        P3S5["5. Read：revert 後<br/>trunk 的建置或 CI 狀態"]
        G_P3S5_1{"狀態為綠？"}
    end
    subgraph P4["Phase 4: 交付整合回報"]
        P4S1["1. Report：向使用者回報整合結果"]
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| P2S1
    G_P1S3_1 -->|否| P1S4
    P1S4 --> P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P2S1
    G_P2S3_1 -->|否| P3S1
    P3S1 --> G_P3S1_1
    G_P3S1_1 -->|是| P3S3
    G_P3S1_1 -->|否| P3S2
    P3S2 --> P3S3
    P3S3 --> G_P3S3_1
    G_P3S3_1 -->|是| P4S1
    G_P3S3_1 -->|否| P3S4
    P3S4 --> P3S5
    P3S5 --> G_P3S5_1
    G_P3S5_1 -->|是| P1S3
    G_P3S5_1 -->|否| P4S1
    P4S1 --> End
```
</details>
