# 跨產出物分析: 線上 1A2B 多人對戰平台

**Feature**: [spec.md](./spec.md) | **Tasks**: [tasks.md](./tasks.md) | **Constitution**: `constitution/`

## 判定

**最新一輪:第 1 輪(2026-10-29)— ⛔ 不能進 `/implement`**

還沒解決的 CRITICAL 有 A1,HIGH 有 A2、A3、A4;另有 2 個 LOW(A5、A6)不擋實作,建議一起修掉。

## 檢查範圍

| 產出物 | 產出的步驟 |
|---|---|
| `spec.md` | `/specify` |
| `research.md`、`techstack.md` | `/technical-research` |
| `plan.md` | `/system-analysis` |
| `contracts/game.asyncapi.yaml` | `/api-plan` |
| `prototype/` | `/ui-plan` |
| `deploy/` | `/deploy-plan` |
| `tasks.md` | `/tasks` |
| `constitution/api-plan/asyncapi.md` | `/constitution` |

---

## 第 1 輪(2026-10-29)

### 前置檢查

| 腳本 | 結果 |
|---|---|
| `specify/scripts/check_spec.py` | ✅ 通過 |
| `system-analysis/scripts/check_plan.py` | ✅ 通過 |
| `tasks/scripts/check_tasks.py` | ✅ 通過 |

### 問題

| ID | 類別 | 嚴重度 | 位置 | 摘要 | 回哪一步 |
|---|---|---|---|---|---|
| A1 | 憲法 | CRITICAL | `constitution/api-plan/asyncapi.md` 〈錯誤一律帶 traceId〉;`contracts/game.asyncapi.yaml` § `components.schemas.Error`;`tasks.md` § T019 | 憲法 MUST 條文要求「AsyncAPI 推送給呼叫者的錯誤訊息 payload,把 `traceId` 列為必填欄位」,`Error` 的 `required` 是 `[type, code, message]`,`properties` 也沒有 `traceId`;T019 照合約把 `sendError(conn, code, message)` 寫成不帶 `traceId` | `/api-plan` |
| A2 | 矛盾 | HIGH | `spec.md` § FR-010;`prototype/game.html` § `[data-state="setup-auto"]`、`#countdown`;`contracts/game.asyncapi.yaml` § `components.schemas.GameSetupStarted` | FR-010 寫「60 秒內設定自己的祕密數字…逾時未設定者,系統必須替他隨機產生一組」,`setupRemainingMs` 的 `maximum` 也是 60000;原型 `setup-auto` 寫「30 秒內沒有設定,系統替你產生了」,`#countdown` 的預設文字是「設定倒數 30 秒」,腳本在沒有截止時間時補 `Date.now() + 30000`。T025 要把原型文字原樣收進 `zh-TW.json`,照原型做會告訴玩家錯的時限;判 HIGH 是因為使用者看到的規則會不同 | `/ui-plan` |
| A3 | 無法實作 | HIGH | `techstack.md` § 一覽;`tasks.md` § T006;`research.md` § R2 | techstack 兩列 TypeScript(前端 `tsc --noEmit --checkJs`、後端)的版本都寫「未定」;R2 決定以 Node 22 原生 type stripping 直接跑 `.ts`,T006 在 `tsconfig.json` 設 `erasableSyntaxOnly: true`,這個選項要 TypeScript 5.8 以上,版本未定時 T006 不知道能不能用 | `/technical-research` |
| A4 | 矛盾 | HIGH | `tasks.md` § T090;`spec.md` § FR-012、NFR-001、假設 | T090「結果畫面下方顯示本房間歷局的獲勝次數排行榜」以 📎 引用 FR-012,但 FR-012 只講「計算每次猜測的結果…即時顯示給房內所有人」;NFR-001 寫「不保留戰績」,假設寫「不保留戰績、排行榜與歷史對局」。T090 追溯不到需求,而且照它做會多出 spec 明確排除的功能;介面覆蓋表與 `prototype/result.html` 也沒有排行榜 | `/tasks` |
| A5 | 矛盾 | LOW | `research.md` § R9;`techstack.md` § 一覽;`prototype/` § 4 個頁面 | R9 的理由寫「畫面只有 3 個:輸入暱稱、房間(等待中)、對局」,techstack 寫「3 個畫面,不用框架」;原型有 `index.html`、`room.html`、`game.html`、`result.html` 4 頁(`states.html` 也列 4 個 `h2` 區段)。照哪一份做,畫面都是原型那 4 頁,不用框架的決策不受影響 | `/technical-research` |
| A6 | 遺漏 | LOW | `plan.md` § 端點盤點;`prototype/game.html` § `body[data-requirements]`;`prototype/result.html` § `body[data-requirements]`;`prototype/room.html` § `body[data-requirements]` | 端點盤點 E1 的需求出處只列 FR-001、004、005、006、008、009、010、012、013、015、019、NFR-004、SC-001;原型 `game.html` 標了 FR-011、FR-016、FR-017、NFR-003,`result.html` 標了 FR-014、FR-018,`room.html` 標了 FR-014、NFR-003,`index.html` 標了 FR-002。前端實際要做這些需求(tasks 也有 T079–T082),只是 plan 的出處沒寫,照哪一份做行為都一樣 | `/system-analysis` |

### 追溯缺口

只列有缺口的需求;其餘需求從規格檔到任務都接得上。

| 需求 | 規格檔元素 | 任務 | 缺口 |
|---|---|---|---|
| FR-010 設定祕密數字 60 秒 | `prototype/game.html` § `[data-state="setup-auto"]`、`#countdown`(秒數錯) | T057、T065 | A2 |
| NFR-001 不保留戰績 | 無 | T090(與需求相反) | A4 |
| FR-011、FR-014、FR-016、FR-017、FR-018 的前端部分 | `prototype/game.html`、`prototype/result.html`(plan 沒列出處) | T079–T082 | A6 |

### 修正順序

1. `/technical-research` 定下 TypeScript 版本(A3,要能用 `erasableSyntaxOnly` 就要 5.8 以上),並把 R9 與 techstack 的「3 個畫面」改成 4 個(A5)
2. `/system-analysis` 把 FR-002、FR-011、FR-014、FR-016、FR-017、FR-018、NFR-003 補進 E1 的需求出處(A6)
3. `/api-plan` 在 `components.schemas.Error` 加上必填的 `traceId`(A1);`/ui-plan` 把 `game.html` 的 `setup-auto`、`#countdown` 與預設截止時間改成 60 秒(A2)
4. `/tasks` 刪掉 T090(A4),並依第 1、3 步的修正重跑:T006 對齊定下的 TypeScript 版本、T019 / T034 加上 `traceId`、T025 收錄改過的原型文字
5. 重跑 `/analyze`
