# /analyze 驗收素材

兩份輸入都取自之前用本 workflow 產出的 1A2B 線上對戰平台(`001-bulls-cows-online`),`plan.md` 已依 `refactor(ui-plan)!` 的遷移說明把 `uiux-plan` 改成 `ui-plan`;三支前置檢查都通過。

| 資料夾 | 用途 |
|---|---|
| `clean/` | 對照組:原件,沒有刻意埋問題 |
| `planted/` | 埋問題組:在原件上刻意埋三個跨檔問題,另加一條憲法 |

## 答案卷(planted)

| # | 類別 | 預期嚴重度 | 位置 | 埋了什麼 | 預期回哪一步 |
|---|---|---|---|---|---|
| P1 | 矛盾 | HIGH | `spec.md` § FR-010;`prototype/game.html` § `#countdown` | 設定祕密數字的倒數,原型寫 30 秒,FR-010 與 AsyncAPI 都是 60 秒 | `/ui-plan` |
| P2 | 憲法 | CRITICAL | `constitution/api-plan/asyncapi.md` 〈錯誤一律帶 traceId〉;`contracts/game.asyncapi.yaml` § `components.schemas.Error` | `Error` 的 `required` 只有 `type`、`code`、`message` | `/api-plan` |
| P3 | 矛盾 | HIGH | `tasks.md` § T090;`spec.md` § 假設 | 排行榜任務以 📎 引用 FR-012;原本預期是「無法追溯 / MEDIUM」,第一次實跑發現 `spec.md` 假設段明寫「不保留戰績、排行榜」,所以是與需求矛盾,改判 HIGH | `/tasks` |

判定:有 CRITICAL / HIGH → ⛔ 不能進 `/implement`。

驗收時把整個資料夾複製到 `tmp/verify/` 再交給不帶脈絡的 subagent 實跑,不要讓它讀到本檔。
