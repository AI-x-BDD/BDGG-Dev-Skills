---
name: trunk-based-development
description: 開始做一個功能、要切分支或決定分支策略、要合併或推送到 remote、修復 production bug 或處理多日變更時,用這支 Skill 依主幹式開發(Trunk-Based Development)規範切分、驗證並整合程式碼;使用者提到主幹開發、trunk-based development、TBD、開 branch、開 PR、merge、push、切分支、長期分支、feature flag、branch by abstraction 時使用。(未驗證)
---

# SOP

## Phase 1: 判定策略與同步環境
1. Read 檢查目前 repo 的 remote 狀態、預設 branch、工作目錄是否有未提交變更,以及 CI 與本機建置指令。
2. Think 依 `rules/開工判斷-規範.md` 評估變更規模與選擇整合風格(直接進 trunk 或短期 branch)。
3. Write 同步 trunk 的最新狀態;若採短期 branch 則由最新 trunk 開出短期 branch。

## Phase 2: 小步開發與本機驗證
1. Write 依 `rules/分支與變更-規範.md` 實作功能或修復並編寫測試,在本機形成 commit;長變更使用 feature flag 或 branch by abstraction 隔絕未完成功能。
2. Write 從 trunk 拉取最新變更並帶入本機;若有未提交變更則加 `--autostash`,並在本機解決衝突。
3. Write 在本機執行完整建置指令(編譯與所有測試),確認全部通過;若失敗則修復至全部通過。

## Phase 3: 整合進 trunk
1. Write 將變更推送到 remote trunk;若走短期 branch 則發起 PR、通過 review 與 CI 後合併回 trunk,並立刻刪除短期 branch。
2. Read 確認 remote trunk 上最新 commit 的建置或 CI 狀態為綠;若為紅燈則立刻 revert 或緊急修復。

## Phase 4: 交付整合回報
1. Ask 依骨架 `templates/整合回報.md` 與範例 `templates/整合回報.example.md` 向使用者回報整合結果,列出切法、整合風格、本機建置證據、trunk 狀態與留下的開關或技術債。
