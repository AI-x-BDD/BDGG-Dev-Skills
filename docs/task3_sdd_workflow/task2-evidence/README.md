# 道館三第二題:三支輔助 Skill 的實際使用證據

示範專案 `project/` 取自 1A2B 線上對戰平台(埋問題組,見 `../analyze-verify/`),專案根目錄有一條憲法 `constitution/api-plan/asyncapi.md`。

| 完成條件 | 證據 |
|---|---|
| `/clarify` 至少實際完成 3~5 次提問與回寫 | `project/specs/001-bulls-cows-online/spec.md` § 釐清紀錄:7 次提問,答案已寫回對應章節 |
| `/analyze` 至少實際找出一次跨產出物的問題,並完成修正 | `analysis.md` 第 1 輪找出 A1(憲法 / CRITICAL:AsyncAPI 的 `Error` 缺 `traceId`),指出回 `/api-plan`;以 `/api-plan` 修正後重跑,第 2 輪標 A1 ✅ 已修正,並抓到修正帶出的下游不一致 A7(T019 未帶 `traceId`) |
| `/constitution` 至少有一條規則被 SDD workflow 中的 Skill 主動讀取與遵守 | `/api-plan` Phase 1 Step 4 以 `constitution_rules.py` 主動讀到〈錯誤一律帶 traceId〉,照條文把 `traceId` 列為 `Error` 的必填欄位(遵守);`/analyze` 讀同一條條文並判出違規(讀取與把關) |

## 怎麼看前後差異

```bash
git log --oneline -- docs/task3_sdd_workflow/task2-evidence
git diff <修正前快照的 commit> <修正後的 commit> -- docs/task3_sdd_workflow/task2-evidence/project
```

修正前快照只有 `/analyze` 第 1 輪;修正後的 commit 同時包含 `/api-plan` 改的 `contracts/game.asyncapi.yaml` 與 `/analyze` 追加的第 2 輪。
