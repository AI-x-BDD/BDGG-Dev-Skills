---
name: skill-engineering-ex
description: 建立新的 Skill，或依使用者對既有 Skill／一組相關 Skills 的不滿意結果，分析根因並重構 SOP、規則、樣板與腳本。需要整體設計、跨步驟優化、刪減重複要求或編排 skill-form-*、skill-derive-* 時使用；已指定單一步驟的局部轉換可直接使用對應 Deriver。由 Codex 開發，作為 skill-engineering 的對照組，用來比較模型能力與架構差異。未驗證。
---

# SOP

## Phase 1: 確認預期成果
1. Read 依 `rules/預期成果-規範.md` 讀取使用者的要求、相關對話與目標 Skill 已有的內容。
2. Think 整理用途、輸入輸出、邊界與成功案例;若是優化既有 Skill → 跳至 Phase 2 Step 1;若是已確認預期的新建 → 跳至 Phase 3 Step 1。
3. Ask 提出新 Skill 的預期成果並補齊影響設計的缺口;若使用者修正預期 → 跳至 Phase 1 Step 2;若已確認 → 跳至 Phase 3 Step 1。

## Phase 2: 確認落差與根因
1. Read 不滿意結果所經過的 Skill 呼叫路徑、部件與可取得的執行紀錄。
2. Think 依 `rules/診斷-規範.md` 重演相關路徑，形成預期、落差、根因與驗收案例的診斷;若既有確認完整涵蓋本診斷 → 跳至 Phase 3 Step 1。
3. Ask 依骨架 `templates/diagnosis.md` 與範例 `templates/diagnosis.example.md` 提出診斷與證據限制，請使用者補充必要資料或確認診斷;若補充資料或不同意診斷 → 跳至 Phase 2 Step 1。

## Phase 3: 提出編排方案
1. Read skill-form-sop 的 SKILL.md 與其 SOP 格式規範。
2. Think 依 `rules/編排方案-規範.md` 設計 SOP 草案與部件操作清單;若既有確認完整涵蓋本方案 → 跳至 Phase 4 Step 1。
3. Ask 依骨架 `templates/proposal.md` 與範例 `templates/proposal.example.md` 提出方案與驗收方式，請使用者確認是否實作;若調整做法 → 跳至 Phase 3 Step 2。

## Phase 4: 實作並整理部件
1. Delegate 依 `rules/委派-規範.md` 轉交 skill-form-sop，依已確認方案寫出或重構目標 SOP 主幹。
2. Delegate 依方案順序轉交對應 Derivers 或 Forms，完成部件轉換與重構。
3. Write 依方案移除已被取代的部件檔案。
4. Delegate 轉交 skill-form-sop，整合資源指標、分支與步驟位址。

## Phase 5: 驗收成果
1. Read 實際寫入的 Skill、相關呼叫端與部件。
2. Delegate 依 `rules/驗收-規範.md` 將驗收案例交給適用的工具或測試 agent 執行，取得實際結果。
3. Think 對照成功條件與整合檢查，判定驗收結果及未通過的原因;若優化時新證據推翻診斷 → 跳至 Phase 2 Step 1;若方案不足 → 跳至 Phase 3 Step 2;若實作不符方案 → 跳至 Phase 4 Step 1。
4. Ask 依骨架 `templates/acceptance.md` 與範例 `templates/acceptance.example.md` 回報變更、驗收證據與未驗證事項，請使用者試用並提供回饋;若回饋顯示預期有落差 → 跳至 Phase 1 Step 1。
