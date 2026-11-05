# Tasks: 線上 1A2B 多人對戰平台

**Input**: `specs/001-bulls-cows-online/` 的設計文件(本 spec package)

**Prerequisites**: plan.md、spec.md、research.md、techstack.md、contracts/game.asyncapi.yaml、deploy/、prototype/

**Tests**: 包含測試任務。理由:spec.md 每個使用者故事都有獨立測試,SC-003–SC-006 要靠測試或腳本量測;research R3、R6、R7、R10 也指定了要守住的測試。

**Organization**: 依使用者故事分 phase;每個故事底下再依 plan.md「端點盤點」的端點分節(E1 前端、E2 後端、E3 部署與網路),外加一節跨端點驗收,最後一張介面覆蓋表。每個任務都會落在某一個端點的程式碼或環境設定裡。

## Format: `[ID] [P?] [Story] Description`,底下接 ⚙ 與 📎 兩行

- **[P]**:可平行執行(不同檔案、不依賴未完成的任務)
- **[Story]**:所屬的使用者故事(US1、US2、US3)
- 每個任務都寫出確切的檔案路徑
- **⚙**:這個任務要做出來或測到的介面元素,做完時這些元素都必須照規格成立:
  - AsyncAPI:`contracts/<介面>.asyncapi.yaml` § `operations.<operationId>`、`components.schemas.<Name>`
  - OpenAPI:`contracts/<介面>.openapi.yaml` § `paths./<路徑>.<method>`、`components.schemas.<Name>`
  - DBML:`contracts/<介面>.dbml` § `Table <名稱>`、`Table <名稱>.<欄位>`
  - 原型:`prototype/<畫面>.html` § CSS 選擇器,狀態寫 `[data-state="<狀態>"]`,區塊寫 `#<id>`
  - 部署:`deploy/compose.yaml` § `services.<名稱>.<欄位>`、`deploy/proxy.conf` § `location <路徑>`、`deploy/Dockerfile` § `<指令>`
  - 沒有碰到任何介面元素的任務(例如工具鏈設定)不寫這一行
- **📎**:做這個任務時要對照的依據:`spec.md` § FR / NFR / SC / 驗收情境、`research.md` § R、`plan.md` § Q 或段落名、`techstack.md` § 段落名
- ⚙ 與 📎 的每個引用都寫到 `§` 後面的錨點;只有原樣複製整個檔案時才寫 `§ 全檔`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 建立 workspaces、工具鏈與 CI 骨架

- [ ] T001 建立根目錄 `package.json`:`"type": "module"`、`"private": true`、`workspaces: ["shared", "backend", "frontend", "e2e"]`;scripts `lint`(eslint)、`format:check`(prettier --check)、`typecheck`(後端 `tsc --noEmit`、前端 `tsc --noEmit --checkJs -p frontend`)、`test`(`node --test "shared/test/**/*.test.ts" "backend/test/**/*.test.ts"`)、`test:e2e`、`verify:score`、`build`、`check:bundle`;devDependencies 照 techstack.md:`vite@8`、`typescript`、`@types/ws`、`@playwright/test@1.64`、`eslint`、`prettier`;不得引入「刻意不用」列出的套件(Socket.IO、Express、Fastify、Redis、React、Vitest、`@sinonjs/fake-timers`)
  - 📎 `techstack.md` § 依賴、§ 刻意不用;`research.md` § R2(`"type": "module"` 消除 `MODULE_TYPELESS_PACKAGE_JSON`)
- [ ] T002 [P] 建立 `shared/package.json`(name `@bco/shared`,`"type": "module"`,`exports` 指向 `./src/*.ts`)與空的 `shared/src/`、`shared/test/`
  - 📎 `plan.md` § Source Code(`shared/`)
- [ ] T003 [P] 建立 `backend/package.json`(name `@bco/backend`,唯一 runtime 依賴 `ws@8.22.0`,依賴 `@bco/shared`;script `start`: `node src/server.ts`)與空的 `backend/src/{http,ws,rooms,views,domain}/`、`backend/test/`
  - 📎 `techstack.md` § 一覽(後端);`research.md` § R2;`plan.md` § Source Code(`backend/`)
- [ ] T004 [P] 建立 `frontend/package.json`(name `@bco/frontend`,零 runtime 依賴;scripts `dev`: `vite`、`build`: `vite build`,產物到 `frontend/dist`)、`frontend/vite.config.js`(dev server 把 `/ws` proxy 到 `ws://localhost:8080`,`ws: true`)與空的 `frontend/src/{pages,components,i18n}/`、`frontend/test/`
  - 📎 `techstack.md` § 一覽(前端);`research.md` § R9;`plan.md` § Source Code(`frontend/`)
- [ ] T005 [P] 建立 `e2e/package.json`(依賴 `@playwright/test`)與 `e2e/playwright.config.ts`:`webServer` 以 `node backend/src/server.ts` 啟動(先 `npm run build --workspace frontend`),環境變數 `SETUP_TIMEOUT_MS=3000`、`TURN_TIMEOUT_MS=3000`、`RESUME_GRACE_MS=3000`、`HEARTBEAT_INTERVAL_MS=1000`,`baseURL` 為 `http://localhost:8080`
  - 📎 `research.md` § R10(計時設定、多 browser context)
- [ ] T006 [P] 建立根目錄 `tsconfig.json`(`strict: true`、`noUncheckedIndexedAccess: true`、`allowImportingTsExtensions: true`、`noEmit: true`、`module`/`moduleResolution: "nodenext"`、`verbatimModuleSyntax: true`、`erasableSyntaxOnly: true`)與 `frontend/tsconfig.json`(`allowJs`、`checkJs`、`strict`,`include: ["src/**/*.js"]`)
  - 📎 `research.md` § R2、§ R9
- [ ] T007 [P] 建立 `eslint.config.js` 與 `.prettierrc.json`:零警告(`--max-warnings 0`);禁止 `@typescript-eslint/no-explicit-any`;對 `backend/src/rooms/matchmaking.ts` 加 `no-restricted-syntax` 禁止 `async` 函式與 `await`
  - 📎 `research.md` § R3(配對中間不得有 `await`)
- [ ] T008 [P] 建立 `.gitlab-ci.yml`:stages `lint` → `typecheck` → `unit` → `verify` → `e2e` → `build`;image `node:22-slim`;`verify` 跑 `npm run verify:score` 與 `npm run check:bundle`;`build` 以 `deploy/Dockerfile` 建 image 並推到 GitLab Registry
  - 📎 `research.md` § R11;`techstack.md` § 新引入與沿用
- [ ] T009 [P] 把 spec package 的 `deploy/compose.yaml`、`deploy/Dockerfile`、`deploy/proxy.conf`、`deploy/.env.example` 複製到 repo 根目錄的 `deploy/`,內容不改
  - ⚙ `deploy/compose.yaml` § 全檔;`deploy/Dockerfile` § 全檔;`deploy/proxy.conf` § 全檔;`deploy/.env.example` § 全檔
  - 📎 `plan.md` § 待決問題 Q14–Q19

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 三個故事都要用到的純函式、協定型別、連線層與前端外殼

**⚠️ CRITICAL**: 本 phase 完成前不得開始任何使用者故事

### Tests for Foundational ⚠️

> 先寫測試,執行並確認失敗,再實作

- [ ] T010 [P] 撰寫 `shared/test/digits.test.ts`:`validateDigits()` 對 `"1234"`、`"0123"` 回 `null`;對 `"1123"` 回 `DIGITS_REPEATED`;對 `"12a4"`、`"123"`、`"12345"`、`""` 回 `DIGITS_FORMAT_INVALID`
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.Digits`
  - 📎 `spec.md` § FR-009;`plan.md` § 待決問題 Q12
- [ ] T011 [P] 撰寫 `shared/test/score.test.ts`:`score("1234", "1356")` 為 `{ a: 1, b: 1 }`、`score("1234", "1234")` 為 `{ a: 4, b: 0 }`、`score("1234", "5678")` 為 `{ a: 0, b: 0 }`、`score("1234", "4321")` 為 `{ a: 0, b: 4 }`、含 0 開頭的案例
  - 📎 `spec.md` § 使用者故事 2 驗收情境 5、§ SC-004;`research.md` § R7
- [ ] T012 [P] 撰寫 `backend/test/ws/validate.test.ts`:`parseClientMessage()` 對非 JSON、非物件、未知 `type`、缺必填欄位、欄位型別錯誤一律回 `INVALID_MESSAGE`;對 6 種玩家訊息的合法樣本回傳型別化的結果
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.MatchStart`、`SessionResume`、`RoomLeave`、`GameStart`、`SecretSet`、`GuessSubmit`
  - 📎 `plan.md` § 待決問題 Q29

### Implementation for Foundational

- [ ] T013 [P] 實作 `shared/src/digits.ts`:`validateDigits(s): "DIGITS_FORMAT_INVALID" | "DIGITS_REPEATED" | null`,規則照合約 `Digits` 的 `^(?!.*(.).*\1)[0-9]{4}$`,但要分得出格式錯與重複;另匯出 `DIGITS_PATTERN`(讓 T010 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.Digits`
  - 📎 `spec.md` § FR-009;`plan.md` § 待決問題 Q12
- [ ] T014 [P] 實作 `shared/src/score.ts`:純函式 `score(secret, guess): { a: number; b: number }`,A = 位置與數字都對,B = 數字對但位置錯(讓 T011 通過)
  - 📎 `spec.md` § FR-012;`research.md` § R7
- [ ] T015 [P] 建立 `shared/src/protocol.ts`:照合約寫出所有訊息與物件的 TypeScript 型別(`ClientMessage` 6 種、`ServerMessage` 14 種、`Room`、`Player`、`GameViewForSelf`、`TurnState`、`GuessEntry`、`Target`、`RevealedSecret`),以及 `ErrorCode` 聯集,值逐字照合約:`INVALID_MESSAGE`、`NICKNAME_EMPTY`、`NICKNAME_TOO_LONG`、`ALREADY_IN_ROOM`、`RESUME_TOKEN_INVALID`、`NOT_IN_ROOM`、`NOT_HOST`、`GAME_IN_PROGRESS`、`NOT_ENOUGH_PLAYERS`、`NOT_SETUP_PHASE`、`SECRET_ALREADY_SET`、`DIGITS_FORMAT_INVALID`、`DIGITS_REPEATED`、`NOT_GUESS_PHASE`、`NOT_YOUR_TURN`;enum 照合約:`Room.status` `waiting | playing`、`Player.connection` `online | disconnected`、`GuessEntry.outcome` `scored | timeout`、`SecretConfirmed.source` `player | auto`、`PlayerEliminated.reason` `left | disconnect_timeout`、`GameEnded.reason` `guessed | last_player_standing`
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas`(全部 30 個)
  - 📎 `plan.md` § 待決問題 Q12
- [ ] T016 [P] 實作 `backend/src/config.ts`:從環境變數讀 `PORT`(預設 8080)、`STATIC_DIR`(預設 `frontend/dist`)、`SETUP_TIMEOUT_MS`、`TURN_TIMEOUT_MS`、`RESUME_GRACE_MS`(預設皆 60000)、`HEARTBEAT_INTERVAL_MS`(預設 15000);非正整數時啟動失敗並說明是哪個變數
  - ⚙ `deploy/compose.yaml` § `services.app.environment`
  - 📎 `research.md` § R10;`plan.md` § 待決問題 Q17
- [ ] T017 [P] 實作 `backend/src/domain/types.ts`:伺服器內部的 `Player`(`id`、`nickname`、`seat`、`resumeToken`、`connection`、`lastSeenAt`、`inGame`)、`Room`(`id`、`status`、`hostSeat`、`players`、`createdAt`、`game?`)、`Game`(`phase: "setup" | "guessing" | "ended"`、`secrets: Map<seat, string>`、`turn`、`currentGuesserSeat`、`deadline`、`history: GuessEntry[]`、`winnerSeat?`)、`Guess`
  - 📎 `spec.md` § 關鍵實體
- [ ] T018 實作 `backend/src/ws/validate.ts`:`parseClientMessage(raw): ClientMessage | { error: "INVALID_MESSAGE" }`,手寫檢查,不加 schema 驗證套件(依賴 T015;讓 T012 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.MatchStart`、`SessionResume`、`RoomLeave`、`GameStart`、`SecretSet`、`GuessSubmit`
  - 📎 `plan.md` § 待決問題 Q29
- [ ] T019 實作 `backend/src/ws/push.ts`:`sendTo(conn, msg: ServerMessage)` 與 `sendError(conn, code, message)`,`message` 是繁體中文說明;所有送出都經過這裡,型別只接受 `ServerMessage`(依賴 T015)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendError`、`components.schemas.Error`
  - 📎 `spec.md` § NFR-004
- [ ] T020 實作 `backend/src/http/static.ts`:以 `node:http` 送 `config.STATIC_DIR` 的檔案(`index.html`、`assets/*`),未知路徑回 `index.html`,擋掉 `..` 路徑穿越;設定正確的 `Content-Type`
  - ⚙ `deploy/proxy.conf` § `location /`;`deploy/compose.yaml` § `services.app.healthcheck`
  - 📎 `research.md` § R2;`plan.md` § 待決問題 Q16、Q17
- [ ] T021 實作 `backend/src/ws/connection.ts`:以 `ws` 的 `WebSocketServer({ noServer: true })` 只接受 `/ws` 的 upgrade,其他路徑 `socket.destroy()`;每 `HEARTBEAT_INTERVAL_MS` 送 ping,下一次 ping 前沒收到 pong 就 `terminate()`,每次 pong 更新 `lastSeenAt`;收到 text frame 交給 `parseClientMessage()` 後丟給 router;`close` 時通知 router(依賴 T016、T018、T019)
  - ⚙ `contracts/game.asyncapi.yaml` § `channels.game`、`info.description`(連線與共通約定);`deploy/proxy.conf` § `location = /ws`
  - 📎 `research.md` § R5
- [ ] T022 實作 `backend/src/ws/router.ts`:依 `type` 分派到 `rooms/` 的用例函式,用例回傳的錯誤碼經 `sendError()` 送回;未實作的 `type` 暫時回 `INVALID_MESSAGE`(依賴 T021)
  - 📎 `plan.md` § Structure Decision(後端分層)
- [ ] T023 實作 `backend/src/server.ts`:建立 `node:http` server,一般請求交給 `http/static.ts`,`upgrade` 交給 `ws/connection.ts`,監聽 `config.PORT`;收到 `SIGTERM` 時關閉
  - ⚙ `deploy/Dockerfile` § `CMD`;`deploy/compose.yaml` § `services.app.expose`
  - 📎 `plan.md` § 待決問題 Q17
- [ ] T024 [P] 建立 `frontend/src/tokens.css`:把原型 `:root` 的變數(9 個顏色、2 個字體、2 個圓角、4 個間距、1 個陰影)原樣搬過來;建立 `frontend/src/styles.css`,把原型其餘選擇器搬過來並只用 `var(--…)`
  - ⚙ `prototype/style.css` § `:root`、§ `:root` 以外的所有選擇器
  - 📎 `research.md` § R9
- [ ] T025 [P] 建立 `frontend/src/i18n/zh-TW.json` 與 `frontend/src/i18n/index.js`(`t(key, params)`):收錄原型的所有介面文字,以及 15 個錯誤碼各自的說明,例如 `NICKNAME_TOO_LONG` →「暱稱最多 12 個字,目前 {n} 個字」、`DIGITS_REPEATED`/`DIGITS_FORMAT_INVALID` →「必須是 4 個互不重複的數字」
  - ⚙ `prototype/index.html` § 所有 `[data-state]` 區塊的文字;`prototype/room.html` § 所有 `[data-state]` 區塊的文字;`prototype/game.html` § 所有 `[data-state]` 區塊的文字;`prototype/result.html` § 所有 `[data-state]` 區塊的文字;`contracts/game.asyncapi.yaml` § `components.schemas.Error`(`code` 的 15 個值)
  - 📎 `spec.md` § NFR-004、§ 使用者故事 2 驗收情境 3;`plan.md` § 待決問題 Q5
- [ ] T026 實作 `frontend/src/connection.js`:依 `location.protocol` 選 `ws:` 或 `wss:`,連 `` `${proto}//${location.host}/ws` ``;提供 `send(msg)`、`on(type, handler)`、連線狀態事件(`connecting` / `open` / `closed`);以 JSDoc 匯入 `shared/src/protocol.ts` 的型別
  - ⚙ `contracts/game.asyncapi.yaml` § `servers`、`channels.game.address`
  - 📎 `plan.md` § 待決問題 Q14、Q22
- [ ] T027 實作 `frontend/index.html` 與 `frontend/src/main.js`:單一頁面外殼,載入 `tokens.css`、`styles.css`;`main.js` 依伺服器訊息切換 `pages/` 的畫面(輸入暱稱 → 房間 → 對局 → 結果),每個畫面匯出 `mount(root, state)` / `unmount()`;連線中顯示載入狀態
  - ⚙ `prototype/states.html` § 4 個 `h2` 區段(輸入暱稱、房間、對局、遊戲結果)
  - 📎 `plan.md` § Structure Decision(前端)

### 介面覆蓋(Foundational)

> 必須覆蓋的介面元素(合約的 operation 與 path、DBML 的 Table、原型的每一個狀態、部署檔的 service 與 location)一個都不能少;實作或測試欄空著就是漏了

| 介面元素 | 實作 | 測試 |
|---|---|---|
| `game.asyncapi.yaml` § `components.schemas.Digits` | T013 | T010 |
| `game.asyncapi.yaml` § `components.schemas.MatchStart`、`SessionResume`、`RoomLeave`、`GameStart`、`SecretSet`、`GuessSubmit`(解析) | T018 | T012 |
| `game.asyncapi.yaml` § `operations.sendError`、`components.schemas.Error` | T015、T019 | T034 |
| `game.asyncapi.yaml` § `channels.game`(`/ws` 升級、心跳) | T021 | T033、T070 |
| `game.asyncapi.yaml` § `servers` | T026 | T028 |
| `prototype/style.css` § `:root`、`@media (max-width: 600px)` | T024 | T086 |
| `prototype/states.html` § 4 個畫面的切換 | T027 | T028 |
| `deploy/proxy.conf` § `location /`;`compose.yaml` § `services.app.healthcheck` | T020 | T045 |

**Checkpoint**: `npm run lint`、`npm run typecheck`、`npm test` 全綠;`node backend/src/server.ts` 能送出前端外殼,`/ws` 能升級、15 秒心跳在運作

---

## Phase 3: User Story 1 - 輸入暱稱並自動配對進房 (Priority: P1) 🎯 MVP

**Goal**: 使用者輸入暱稱後自動加入未滿的等待中房間或開新房當房主;房內即時看到名單、座位、房主,可以離開

**Independent Test**: 用 5 個瀏覽器分頁依序配對 → 第 1 個分頁開出新房間並成為房主 → 第 2 到 4 個分頁加入同一間房,每個分頁都看到相同的 4 人名單與座位 → 第 5 個分頁被放進另一間新房間並成為那間的房主

### 跨端點驗收(`e2e/`)

> 先寫,確認失敗;本故事的 E2、E1 都完成後才會轉綠

- [ ] T028 [P] [US1] 撰寫 `e2e/tests/us1-matchmaking.spec.ts`:5 個 browser context 依序配對,照 Independent Test 斷言名單、座位、房主標示;另測暱稱空白與 13 個字的提示文字,以及房主離開後房主標示移到下一位
  - ⚙ `prototype/index.html` § `[data-state="nickname-empty"]`、`[data-state="nickname-long"]`;`prototype/room.html` § `#seat-list`、`[data-state="host-transferred"]`;`contracts/game.asyncapi.yaml` § `servers`
  - 📎 `spec.md` § 使用者故事 1 獨立測試、驗收情境 1–5;`research.md` § R10

### E2 後端(WebSocket 訊息協定,`backend/`)

#### 測試

- [ ] T029 [P] [US1] 撰寫 `backend/test/domain/nickname.test.ts`:`normalizeNickname()` 去除前後空白後為空回 `NICKNAME_EMPTY`;超過 12 個 Unicode 字元(以 `[...s].length` 計,含 emoji)回 `NICKNAME_TOO_LONG`;剛好 12 個字(如「週五晚上只想猜數字的人類」)通過;`dedupeNickname("小明", ["小明"])` 為「小明 (2)」,已有「小明」「小明 (2)」時為「小明 (3)」
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.MatchStart`(`nickname`)
  - 📎 `spec.md` § FR-001、FR-005
- [ ] T030 [P] [US1] 撰寫 `backend/test/domain/seats.test.ts`:`nextFreeSeat([1, 2])` 為 3、`nextFreeSeat([1, 3])` 為 2、`nextFreeSeat([1, 2, 3, 4])` 為 `null`;`nextHostSeat([2, 4])` 為 2
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.Seat`
  - 📎 `spec.md` § FR-004、FR-006;`plan.md` § 待決問題 Q1、Q9
- [ ] T031 [P] [US1] 撰寫 `backend/test/rooms/matchmaking.test.ts`:沒有等待房時開新房、送出者坐 1 號且為房主(情境 1);有 2 人的等待房時加入並坐 3 號(情境 2);唯一的等待房已滿 4 人時另開新房(情境 3);`playing` 的房間不會被配到;已在房間裡的連線再送 `match.start` 回 `ALREADY_IN_ROOM`
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveMatchStart`
  - 📎 `spec.md` § 使用者故事 1 驗收情境 1–3、§ FR-002、FR-007
- [ ] T032 [P] [US1] 撰寫 `backend/test/rooms/leave.test.ts`:等待中 3 人房主離開 → 房主轉給座位號最小的玩家、其餘人收到 `room.updated`(情境 4);只剩房主一人離開 → 房間從配對池移除(情境 5);1、2、3 號中 2 號離開後新進的人坐 2 號;不在房間的連線送 `room.leave` 回 `NOT_IN_ROOM`
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveRoomLeave`、`operations.sendRoomUpdated`
  - 📎 `spec.md` § 使用者故事 1 驗收情境 4–5、§ FR-006;`plan.md` § 待決問題 Q1
- [ ] T033 [P] [US1] 撰寫 `backend/test/integration/matchmaking-concurrency.test.ts`:啟動真實 server,400 個 Node 內建 `WebSocket` client 同時送 `match.start`,斷言剛好 100 間房、每間 ≤ 4 人、1 人房 0 間;附對照組:以測試替身在「找房」與「入座」之間插入 `await`,斷言這個測試會失敗(證明測得到競態)
  - ⚙ `contracts/game.asyncapi.yaml` § `channels.game`、`operations.receiveMatchStart`
  - 📎 `spec.md` § FR-003、SC-003;`research.md` § R3
- [ ] T034 [P] [US1] 撰寫 `backend/test/contract/us1-messages.test.ts`:對 `match.joined`、`room.updated`、`room.left`、`error` 逐欄手寫斷言必填欄位與 enum 值符合合約,不新增 schema 驗證套件
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.MatchJoined`、`RoomUpdated`、`RoomLeft`、`Room`、`Player`、`ResumeToken`、`Error`
  - 📎 `plan.md` § 待決問題 Q29

#### 實作

- [ ] T035 [P] [US1] 實作 `backend/src/domain/nickname.ts`:`normalizeNickname(raw)`(trim 後以 Unicode 字元計 1–12 個字)與 `dedupeNickname(name, existing)`(讓 T029 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.MatchStart`(`nickname`)
  - 📎 `spec.md` § FR-001、FR-005
- [ ] T036 [P] [US1] 實作 `backend/src/domain/seats.ts`:`nextFreeSeat(occupied)`、`nextHostSeat(seats)`,座位號 1–4,不重排(讓 T030 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.Seat`
  - 📎 `plan.md` § 待決問題 Q1、Q9
- [ ] T037 [US1] 實作 `backend/src/rooms/registry.ts`:記憶體中的房間表、連線 → 玩家對應、`resumeToken` → 玩家對應(token 用 `crypto.randomUUID()`);房間關閉時一併清掉。合約沒有「已關閉」狀態,spec 的「已關閉」就是從 registry 移除
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.ResumeToken`
  - 📎 `research.md` § R3、§ R5(重連身分)
- [ ] T038 [US1] 實作 `backend/src/rooms/matchmaking.ts`:`matchStart(conn, nickname)` **整段同步、不得有 `await`**:驗證暱稱 → 找第一間 `waiting` 且未滿 4 人的房間,沒有就開新房並設房主 → `nextFreeSeat()` 入座 → `dedupeNickname()` → 送 `match.joined` 給本人、`room.updated` 給房內所有人(讓 T031、T033 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveMatchStart`、`operations.sendMatchJoined`、`operations.sendRoomUpdated`
  - 📎 `spec.md` § FR-002–FR-005、FR-007;`research.md` § R3
- [ ] T039 [US1] 實作 `backend/src/rooms/leave.ts` 的等待中路徑:`roomLeave(conn)` 移除玩家、送 `room.left` 給本人;房主離開時 `hostSeat = nextHostSeat()`;最後一人離開時關閉房間;其餘人收到 `room.updated`(讓 T032 通過)。斷線(`close`)暫時視同離開,US3 會改成保留 60 秒
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveRoomLeave`、`operations.sendRoomLeft`、`operations.sendRoomUpdated`
  - 📎 `spec.md` § FR-006
- [ ] T040 [US1] 實作 `backend/src/views/room-view.ts`:把內部 `Room` 轉成合約的 `Room`(`status`、`hostSeat`、依座位號排序的 `players`),不含任何 token 或祕密數字;在 `backend/src/ws/router.ts` 接上 `match.start`、`room.leave`(讓 T034 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.Room`、`Player`
  - 📎 `research.md` § R6

### E1 前端(畫面與互動,`frontend/`)

> 可與 E2 平行:先照合約與 `prototype/mock.js` 的假資料把畫面做出來,E2 完成後再接真實訊息

- [ ] T041 [P] [US1] 實作 `frontend/src/pages/nickname.js`:照原型的版面與 5 個狀態;允許輸入超過 12 個字,送出時才以紅字顯示「最多 12 個字,目前 N 個字」;送出 `match.start`,收到 `error` 時以 `t()` 顯示對應說明;收到 `match.joined` 時把 `resumeToken` 存進 `sessionStorage`(不得用 `localStorage`),用 try/catch 包住
  - ⚙ `prototype/index.html` § `#match-form`、`[data-state="normal"]`、`[data-state="nickname-empty"]`、`[data-state="nickname-long"]`、`[data-state="loading"]`、`[data-state="error"]`;`contracts/game.asyncapi.yaml` § `operations.receiveMatchStart`、`operations.sendMatchJoined`
  - 📎 `plan.md` § 待決問題 Q5;`research.md` § R5
- [ ] T042 [P] [US1] 實作 `frontend/src/components/player-list.js`:依座位號列出 1–4 號,空座位顯示空位,房主加標示,自己加「你」;同名者照伺服器給的「小明 (2)」顯示
  - ⚙ `prototype/room.html` § `#seat-list`;`contracts/game.asyncapi.yaml` § `components.schemas.Player`
  - 📎 `spec.md` § FR-004、FR-005
- [ ] T043 [US1] 實作 `frontend/src/pages/room.js`:照原型的版面與狀態;收到 `room.updated` 即時重畫 `player-list`;「離開房間」送 `room.leave`,收到 `room.left` 回到暱稱畫面並清掉 `sessionStorage` 的 token(依賴 T042)
  - ⚙ `prototype/room.html` § `[data-state="alone"]`、`[data-state="host-ready"]`、`[data-state="guest"]`、`[data-state="host-transferred"]`、`[data-state="seat-refill"]`、`[data-state="loading"]`、`#leave-room`;`contracts/game.asyncapi.yaml` § `operations.sendRoomUpdated`、`operations.receiveRoomLeave`、`operations.sendRoomLeft`
  - 📎 `spec.md` § FR-006
- [ ] T044 [US1] 在 `frontend/src/main.js` 接上 US1 的畫面切換:`match.joined` → 房間、`room.left` → 暱稱
  - ⚙ `prototype/states.html` § 「輸入暱稱」「房間」兩個 `h2` 區段
  - 📎 `spec.md` § 使用者故事 1 驗收情境 1

### E3 部署與網路(對外入口,`deploy/`)

- [ ] T045 [US1] 以 `docker compose -f deploy/compose.yaml up --build` 啟動,確認 `proxy` 與 `app` 的 healthcheck 都變 healthy,經 `http://localhost:${PUBLIC_PORT:-8080}/` 用兩個瀏覽器分頁配對進同一房(確認 `/` 與 `/ws` 都經 nginx 轉發、Upgrade 成功);結果記錄在 `docs/deploy-check.md`
  - ⚙ `deploy/compose.yaml` § `services.proxy.ports`、`services.proxy.healthcheck`、`services.app.healthcheck`;`deploy/proxy.conf` § `location /`、`location = /ws`;`deploy/Dockerfile` § `CMD`
  - 📎 `plan.md` § 待決問題 Q15–Q18

### 介面覆蓋(US1)

> 必須覆蓋的介面元素(合約的 operation 與 path、DBML 的 Table、原型的每一個狀態、部署檔的 service 與 location)一個都不能少;實作或測試欄空著就是漏了

| 介面元素 | 實作 | 測試 |
|---|---|---|
| `game.asyncapi.yaml` § `operations.receiveMatchStart` | T038、T041 | T031、T033 |
| `game.asyncapi.yaml` § `operations.sendMatchJoined` | T038、T041 | T034 |
| `game.asyncapi.yaml` § `operations.sendRoomUpdated` | T038、T039、T043 | T032、T034 |
| `game.asyncapi.yaml` § `operations.receiveRoomLeave`(等待中) | T039、T043 | T032 |
| `game.asyncapi.yaml` § `operations.sendRoomLeft` | T039、T043 | T034 |
| `game.asyncapi.yaml` § `components.schemas.Room`、`Player` | T040、T042 | T034 |
| `game.asyncapi.yaml` § `components.schemas.Seat` | T036 | T030 |
| `game.asyncapi.yaml` § `components.schemas.ResumeToken` | T037 | T034 |
| `prototype/index.html` § `[data-state="normal"]`、`nickname-empty`、`nickname-long`、`loading`、`error` | T041 | T028 |
| `prototype/room.html` § `[data-state="alone"]`、`host-ready`、`guest`、`host-transferred`、`seat-refill`、`loading` | T043 | T028 |
| `prototype/room.html` § `#seat-list` | T042 | T028 |
| `deploy/compose.yaml` § `services.proxy`、`services.app`;`proxy.conf` § `location /`、`location = /ws` | T009 | T045 |

**Checkpoint**: US1 可獨立運作;T028–T034 全綠,手動用 5 個分頁跑一次 Independent Test,且 MVP 已能經 compose 部署

---

## Phase 4: User Story 2 - 設定祕密數字並輪流猜下一位 (Priority: P2)

**Goal**: 房主在 2–4 人時開始;每人在 60 秒內設定祕密數字(逾時代設),之後從座位號最小的玩家開始依座位輪流猜下一位,伺服器回報幾 A 幾 B,第一個猜中的人獲勝並公開所有數字,房間回到等待中

**Independent Test**: 在一間已有 3 人的房間,房主開始遊戲 → 3 人分別設定 1234、5678、9012 → 依座位輪流猜,確認每次的幾 A 幾 B 正確、所有人看到相同的猜測紀錄、任何人在結束前都看不到別人的祕密數字 → 有人猜中時遊戲立即結束並公開三組數字

### 跨端點驗收(`e2e/`、`scripts/`)

> 先寫,確認失敗;本故事的 E2、E1 都完成後才會轉綠

- [ ] T046 [P] [US2] 撰寫 `e2e/tests/us2-game.spec.ts`:3 個 browser context 照 Independent Test 跑一局;用 `page.on("websocket")` 收集每個分頁收到的所有訊息原文,結束前搜尋其他玩家的祕密數字,命中必須是 0;另測 1 人時「開始遊戲」不可按並顯示至少需要 2 人、非房主看不到按鈕(情境 1)
  - ⚙ `prototype/room.html` § `.js-start`、`[data-state="alone"]`、`[data-state="guest"]`;`prototype/game.html` § `[data-state="setup"]`、`[data-state="setup-done"]`、`[data-state="my-turn"]`、`[data-state="waiting-turn"]`、`#log`;`prototype/result.html` § `[data-state="win"]`、`[data-state="lose"]`、`#reveal`
  - 📎 `spec.md` § 使用者故事 2 獨立測試、驗收情境 1、§ SC-005;`research.md` § R6
- [ ] T047 [P] [US2] 撰寫 `scripts/verify-score.ts`:窮舉 5 040 × 5 040 組合法數字,拿另一種寫法的參考實作與 `shared/src/score.ts` 比對,不一致數必須為 0,否則 exit 1;加 `--inject-fault` 參數讓參考實作故意錯一組,證明腳本抓得到
  - 📎 `spec.md` § SC-004;`research.md` § R7

### E2 後端(WebSocket 訊息協定,`backend/`)

#### 測試

- [ ] T048 [P] [US2] 撰寫 `backend/test/domain/targets.test.ts`:`buildTargets([1, 2, 3])` 為 1→2、2→3、3→1;`buildTargets([1, 2])` 為 1→2、2→1(2 人互猜);`buildTargets([1, 3, 4])` 為 1→3、3→4、4→1;`nextGuesser([1, 2, 3], 3)` 為 1
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.Target`
  - 📎 `spec.md` § FR-011、FR-019、§ 邊界情況
- [ ] T049 [P] [US2] 撰寫 `backend/test/rooms/game-start.test.ts`:1 人房房主送 `game.start` 回 `NOT_ENOUGH_PLAYERS`;非房主送回 `NOT_HOST`;`playing` 時再送回 `GAME_IN_PROGRESS`;2–4 人時所有人收到 `game.setupStarted`(`setupRemainingMs` 為 60000、`targets` 照座位圈),房間不再被配對到
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveGameStart`、`operations.sendGameSetupStarted`
  - 📎 `spec.md` § FR-007、FR-008、NFR-005
- [ ] T050 [P] [US2] 撰寫 `backend/test/rooms/secret.test.ts`:`secret.set` 合法時只有本人收到 `secret.confirmed`(`source: "player"`)、所有人收到只含座位號的 `game.setupProgress`;`"1123"` 回 `DIGITS_REPEATED`、`"12a4"` 回 `DIGITS_FORMAT_INVALID`;再送一次回 `SECRET_ALREADY_SET`;猜測階段送回 `NOT_SETUP_PHASE`;以 `mock.timers.enable({ apis: ["setTimeout", "Date"] })` 快轉 59 999ms 不觸發、再 1ms 時未設定者收到 `secret.confirmed`(`source: "auto"`,合法數字),其他人收不到這組數字
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveSecretSet`、`operations.sendSecretConfirmed`、`operations.sendSetupProgress`
  - 📎 `spec.md` § FR-009、FR-010;`plan.md` § 待決問題 Q10;`research.md` § R4
- [ ] T051 [P] [US2] 撰寫 `backend/test/rooms/guess.test.ts`:全員設定完成後所有人收到 `turn.started`(`turn: 1`、`guesserSeat` 為座位號最小的玩家)(情境 4);非輪到的人送 `guess.submit` 回 `NOT_YOUR_TURN`(含同一回合重送);設定階段送回 `NOT_GUESS_PHASE`;B 的數字是 1234、A 猜 1356 → 所有人收到 `guess.result`,`entry` 為 `outcome: "scored"`、`a: 1`、`b: 1`(情境 5);重複送出相同猜測照常計算一回合;猜中 4A0B → 所有人收到 `game.ended`(`reason: "guessed"`)且房間回到 `waiting`、房主可再開一局、新玩家可再被配進來(情境 6、7)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendTurnStarted`、`operations.receiveGuessSubmit`、`operations.sendGuessResult`、`operations.sendGameEnded`
  - 📎 `spec.md` § 使用者故事 2 驗收情境 4–7、§ FR-011–FR-014、§ 邊界情況
- [ ] T052 [P] [US2] 撰寫 `backend/test/views/no-leak.test.ts`:對設定階段與猜測階段的每一種推送,逐一檢查每位玩家收到的 JSON 原文,不得出現其他玩家的祕密數字字串;只有 `game.ended` 例外
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendGameSetupStarted`、`sendSecretConfirmed`、`sendSetupProgress`、`sendTurnStarted`、`sendGuessResult`
  - 📎 `spec.md` § NFR-002、SC-005;`research.md` § R6
- [ ] T053 [P] [US2] 撰寫 `backend/test/contract/us2-messages.test.ts`:對 6 種推送逐欄手寫斷言必填欄位、enum 值與範圍(`*RemainingMs` 介於 0–60000、`a`/`b` 介於 0–4、`turn` ≥ 1)
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.GameSetupStarted`、`SecretConfirmed`、`SetupProgress`、`TurnStarted`、`GuessResult`、`GuessEntry`、`GameEnded`、`RevealedSecret`、`Target`
  - 📎 `plan.md` § 待決問題 Q29

#### 實作

- [ ] T054 [P] [US2] 實作 `backend/src/domain/targets.ts`:`buildTargets(inGameSeats)`(下一位仍在局的玩家,最後一位接回最前面)、`nextGuesser(inGameSeats, currentSeat)`(讓 T048 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.Target`
  - 📎 `spec.md` § FR-019
- [ ] T055 [P] [US2] 實作 `backend/src/rooms/timers.ts`:每間房一個 `setTimeout` 的截止時間管理,`schedule(room, kind, ms, fn)`、`cancel(room, kind)`、`remainingMs(room, kind)`;只用 `setTimeout` 與 `Date.now()`,讓 `mock.timers` 能快轉
  - 📎 `research.md` § R4
- [ ] T056 [US2] 實作 `backend/src/rooms/game.ts` 的開局:`gameStart(conn)` 檢查房主與 2–4 人(斷線保留中的玩家也算人數),建立 `Game`(`phase: "setup"`)、`status = "playing"`、排設定倒數,送 `game.setupStarted`(讓 T049 通過;依賴 T054、T055)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveGameStart`、`operations.sendGameSetupStarted`
  - 📎 `spec.md` § FR-008;`plan.md` § 待決問題 Q8
- [ ] T057 [US2] 實作 `backend/src/rooms/game.ts` 的設定祕密數字:`secretSet(conn, secret)` 以 `validateDigits()` 驗證、鎖定後不能改;設定倒數到期時以 `crypto.randomInt` 替未設定者產生合法數字;全員設定完成時取消倒數、進入 `guessing`,`turn = 1`、`currentGuesserSeat` 為座位號最小的在局玩家,送 `turn.started`(讓 T050 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveSecretSet`、`operations.sendSecretConfirmed`、`operations.sendSetupProgress`、`operations.sendTurnStarted`
  - 📎 `spec.md` § FR-009、FR-010;`research.md` § R6;`plan.md` § 待決問題 Q9、Q10
- [ ] T058 [US2] 實作 `backend/src/rooms/game.ts` 的猜測:`guessSubmit(conn, guess)` 只受理 `currentGuesserSeat` 的一次猜測,以 `shared/src/score.ts` 計算,寫入 `history` 並送 `guess.result`;4A0B 時呼叫 `endGame(room, winnerSeat, "guessed")`,否則換 `nextGuesser()` 並送 `turn.started`(讓 T051 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveGuessSubmit`、`operations.sendGuessResult`、`operations.sendTurnStarted`、`components.schemas.GuessEntry`
  - 📎 `spec.md` § FR-011–FR-013
- [ ] T059 [US2] 實作 `backend/src/rooms/game.ts` 的 `endGame(room, winnerSeat, reason)`:取消所有對局計時、送 `game.ended`(`secrets` 只列已定下數字的玩家)、清掉 `room.game`、`status = "waiting"`,讓房間回到配對池
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendGameEnded`、`components.schemas.RevealedSecret`
  - 📎 `spec.md` § FR-013、FR-014;`plan.md` § 待決問題 Q13
- [ ] T060 [US2] 實作 `backend/src/views/player-view.ts`:`setupStartedFor(player)`、`secretConfirmedFor(player)`、`setupProgressFor(room)`、`turnStartedFor(room)`、`guessResultFor(entry)`、`gameEndedFor(room)`,以及 US3 會用到的 `gameViewForSelf(room, player)`(只含本人的 `mySecret`);`backend/src/rooms/game.ts` 只能透過這裡產生推送內容(讓 T052、T053 通過);在 `backend/src/ws/router.ts` 接上 `game.start`、`secret.set`、`guess.submit`
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.GameSetupStarted`、`SecretConfirmed`、`SetupProgress`、`TurnStarted`、`GuessResult`、`GameEnded`、`GameViewForSelf`、`TurnState`
  - 📎 `research.md` § R6

### E1 前端(畫面與互動,`frontend/`)

> 可與 E2 平行:先照合約與 `prototype/mock.js` 的假資料把畫面做出來,E2 完成後再接真實訊息

- [ ] T061 [P] [US2] 實作 `frontend/src/components/countdown.js`:收到 `*RemainingMs` 後以 `requestAnimationFrame` 從本地 `performance.now()` 往下數,只負責顯示,到 0 也不送任何訊息
  - ⚙ `prototype/game.html` § `#countdown`;`contracts/game.asyncapi.yaml` § `components.schemas.GameSetupStarted`(`setupRemainingMs`)、`TurnStarted`(`turnRemainingMs`)
  - 📎 `spec.md` § NFR-005;`research.md` § R4
- [ ] T062 [P] [US2] 實作 `frontend/src/components/guess-history.js`:顯示猜測者、被猜者、猜測內容與「幾 A 幾 B」或「逾時」,數字用等寬字;最新的在最上面
  - ⚙ `prototype/game.html` § `#log`;`contracts/game.asyncapi.yaml` § `components.schemas.GuessEntry`
  - 📎 `plan.md` § 待決問題 Q24
- [ ] T063 [P] [US2] 實作 `frontend/src/components/target-ring.js`:顯示「你要猜:N 號 某某」「N 號 某某 在猜你的數字」,並列出整圈誰猜誰
  - ⚙ `prototype/game.html` § `#my-target`、`#guessed-by`、`#ring`;`contracts/game.asyncapi.yaml` § `components.schemas.Target`
  - 📎 `spec.md` § FR-019;`plan.md` § 待決問題 Q6
- [ ] T064 [US2] 在 `frontend/src/pages/room.js` 加入「開始遊戲」:只有房主看得到;少於 2 人時不可按並提示「至少需要 2 人」;按下送 `game.start`
  - ⚙ `prototype/room.html` § `.js-start`、`[data-state="alone"]`、`[data-state="host-ready"]`、`[data-state="guest"]`;`contracts/game.asyncapi.yaml` § `operations.receiveGameStart`
  - 📎 `spec.md` § 使用者故事 2 驗收情境 1、§ FR-008
- [ ] T065 [US2] 實作 `frontend/src/pages/game.js`:照原型的版面與狀態;設定與猜測的輸入框先在前端用 `shared/src/digits.ts` 提示,但以伺服器的 `error` 為準;代設數字時停 3 秒讓本人看清楚;非輪到的人看到「等待 N 號猜測」(依賴 T061–T063)
  - ⚙ `prototype/game.html` § `[data-state="setup"]`、`[data-state="setup-invalid"]`、`[data-state="setup-done"]`、`[data-state="setup-auto"]`、`[data-state="my-turn"]`、`[data-state="guess-invalid"]`、`[data-state="waiting-turn"]`、`.js-secret-form`、`.js-guess-form`;`contracts/game.asyncapi.yaml` § `operations.sendGameSetupStarted`、`receiveSecretSet`、`sendSecretConfirmed`、`sendSetupProgress`、`sendTurnStarted`、`receiveGuessSubmit`、`sendGuessResult`
  - 📎 `plan.md` § 待決問題 Q23
- [ ] T066 [US2] 實作 `frontend/src/pages/result.js`:顯示獲勝者與每個人的祕密數字;停在結果頁,按「回到房間」才回房間畫面;有人猜中時對局畫面先顯示「X 猜中了」1.5 秒再進結果頁
  - ⚙ `prototype/result.html` § `[data-state="win"]`、`[data-state="lose"]`、`#reveal`、`#back-to-room`;`contracts/game.asyncapi.yaml` § `operations.sendGameEnded`、`components.schemas.RevealedSecret`
  - 📎 `plan.md` § 待決問題 Q4、Q27
- [ ] T067 [US2] 在 `frontend/src/main.js` 接上 US2 的畫面切換:`game.setupStarted` → 對局、`game.ended` → 結果、「回到房間」→ 房間
  - ⚙ `prototype/states.html` § 「對局」「遊戲結果」兩個 `h2` 區段
  - 📎 `spec.md` § FR-014

### E3 部署與網路(對外入口,`deploy/`)

本故事沒有新的對外入口、路徑或環境變數,不改 `deploy/`。

### 介面覆蓋(US2)

> 必須覆蓋的介面元素(合約的 operation 與 path、DBML 的 Table、原型的每一個狀態、部署檔的 service 與 location)一個都不能少;實作或測試欄空著就是漏了

| 介面元素 | 實作 | 測試 |
|---|---|---|
| `game.asyncapi.yaml` § `operations.receiveGameStart` | T056、T064 | T049 |
| `game.asyncapi.yaml` § `operations.sendGameSetupStarted` | T056、T060、T065 | T049、T053 |
| `game.asyncapi.yaml` § `operations.receiveSecretSet` | T057、T065 | T050 |
| `game.asyncapi.yaml` § `operations.sendSecretConfirmed` | T057、T060、T065 | T050、T053 |
| `game.asyncapi.yaml` § `operations.sendSetupProgress` | T057、T060、T065 | T050、T053 |
| `game.asyncapi.yaml` § `operations.sendTurnStarted` | T057、T058、T060、T065 | T051、T053 |
| `game.asyncapi.yaml` § `operations.receiveGuessSubmit` | T058、T065 | T051 |
| `game.asyncapi.yaml` § `operations.sendGuessResult` | T058、T060、T065 | T051、T053 |
| `game.asyncapi.yaml` § `operations.sendGameEnded`(`reason: "guessed"`) | T059、T060、T066 | T051、T053 |
| `game.asyncapi.yaml` § `components.schemas.Target` | T054、T063 | T048 |
| `game.asyncapi.yaml` § `components.schemas.GuessEntry` | T058、T062 | T053 |
| `game.asyncapi.yaml` § `components.schemas.RevealedSecret` | T059、T066 | T053 |
| `prototype/room.html` § `.js-start` | T064 | T046 |
| `prototype/game.html` § `[data-state="setup"]`、`setup-invalid`、`setup-done`、`setup-auto`、`my-turn`、`guess-invalid`、`waiting-turn` | T065 | T046 |
| `prototype/game.html` § `#countdown`、`#log`、`#my-target`、`#guessed-by`、`#ring` | T061、T062、T063 | T046 |
| `prototype/result.html` § `[data-state="win"]`、`lose` | T066 | T046 |

**Checkpoint**: US1 與 US2 都可獨立運作;`npm run verify:score` 不一致 0 組、`--inject-fault` 時不一致 1 組;3 人局手動跑一次 Independent Test

---

## Phase 5: User Story 3 - 逾時、斷線與中途離開 (Priority: P3)

**Goal**: 有人掛機、斷線或中途離開時也能把局玩完:回合逾時跳過;斷線保留座位 60 秒可重連;逾時或主動離開判出局並重新接圈;只剩 1 人時獲勝

**Independent Test**: 4 人開局 → 輪到 2 號時放著不動,60 秒後確認輪到 3 號 → 關閉 3 號分頁並在 30 秒內重開,確認回到原座位且看得到完整猜測紀錄 → 關閉 4 號分頁超過 60 秒,確認 4 號出局、3 號改猜 1 號 → 再讓 1、3 號離開,確認剩下的 2 號獲勝

### 跨端點驗收(`e2e/`)

> 先寫,確認失敗;本故事的 E2、E1 都完成後才會轉綠

- [ ] T068 [P] [US3] 撰寫 `e2e/tests/us3-resilience.spec.ts`:4 個 browser context 照 Independent Test 跑(用 T005 的 3 秒短時限);重新整理分頁視同斷線重連,回到原座位;遊戲中按「離開」要先出現確認框
  - ⚙ `prototype/game.html` § `[data-state="timeout"]`、`[data-state="reconnecting"]`、`[data-state="eliminated"]`、`[data-state="leave-confirm"]`;`prototype/room.html` § `[data-state="disconnected"]`;`prototype/result.html` § `[data-state="last-one"]`
  - 📎 `spec.md` § 使用者故事 3 獨立測試、驗收情境 1–5;`plan.md` § 待決問題 Q3;`research.md` § R10

### E2 後端(WebSocket 訊息協定,`backend/`)

#### 測試

- [ ] T069 [P] [US3] 撰寫 `backend/test/rooms/turn-timeout.test.ts`:以 `mock.timers` 快轉 60 000ms,輪到的人沒送出 → 所有人收到 `turn.skipped`(`entry.outcome: "timeout"`,沒有 `guess`/`a`/`b`),接著收到下一位的 `turn.started`,逾時的人仍在局(情境 1);輪到的人斷線時倒數照算,逾時一樣跳過(情境 5)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendTurnSkipped`、`operations.sendTurnStarted`
  - 📎 `spec.md` § 使用者故事 3 驗收情境 1、5、§ FR-015;`research.md` § R4
- [ ] T070 [P] [US3] 撰寫 `backend/test/rooms/resume.test.ts`:遊戲中斷線 → 其他人收到 `room.updated` 且該玩家 `connection: "disconnected"`;30 秒內以同一 `resumeToken` 送 `session.resume` → 收到 `session.resumed`(`mySeat` 不變、`game.mySecret` 是自己的數字、`game.history` 完整),倒數不重設;等待中斷線也保留 60 秒並照樣佔座位、算進開局人數,房主斷線時保留期間 `hostSeat` 不變;超過 60 秒或不認得的 token 回 `RESUME_TOKEN_INVALID`;保留時間從最後一次 pong 起算
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveSessionResume`、`operations.sendSessionResumed`、`operations.sendRoomUpdated`、`components.schemas.GameViewForSelf`、`channels.game`(心跳)
  - 📎 `spec.md` § 使用者故事 3 驗收情境 2、§ FR-016;`plan.md` § 待決問題 Q8、Q28
- [ ] T071 [P] [US3] 撰寫 `backend/test/rooms/session-replaced.test.ts`:同一 `resumeToken` 在線時另一條連線送 `session.resume` → 舊連線收到 `session.replaced` 後被關閉,新連線接手座位
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendSessionReplaced`
  - 📎 `plan.md` § 待決問題 Q11
- [ ] T072 [P] [US3] 撰寫 `backend/test/rooms/elimination.test.ts`:4 人局 3 號斷線超過 60 秒 → 所有人收到 `player.eliminated`(`seat: 3`、`nickname`、`reason: "disconnect_timeout"`、`targets` 中 2→4)(情境 3);遊戲中送 `room.leave` → `reason: "left"`,本人收到 `room.left`;只剩 2 人時一人離開 → 剩下的人收到 `game.ended`(`reason: "last_player_standing"`)(情境 4);輪到的人出局時直接換下一位並送 `turn.started`;設定階段有人離開到只剩 1 人 → 直接獲勝,`secrets` 只含已定下的數字;出局玩家的數字不再被猜;等待中斷線超過 60 秒視同離開,斷線的是房主時此時才轉給座位號最小的玩家
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveRoomLeave`、`operations.sendPlayerEliminated`、`operations.sendGameEnded`
  - 📎 `spec.md` § 使用者故事 3 驗收情境 3–4、§ FR-017、FR-018、§ 邊界情況;`plan.md` § 待決問題 Q13、Q28
- [ ] T073 [P] [US3] 撰寫 `backend/test/integration/no-stuck-game.test.ts`:以 `mock.timers` 對「全員掛機」「全員斷線」「輪流離開」「設定階段全員斷線」各跑一次,斷言每一局最後都收到 `game.ended` 或回到可繼續的狀態,沒有計時器殘留
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendGameEnded`
  - 📎 `spec.md` § SC-006
- [ ] T074 [P] [US3] 撰寫 `backend/test/contract/us3-messages.test.ts`:對 `session.resumed`(含 `GameViewForSelf` 的必填欄位)、`session.replaced`、`turn.skipped`、`player.eliminated` 逐欄手寫斷言必填欄位與 enum 值
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.SessionResumed`、`GameViewForSelf`、`TurnState`、`SessionReplaced`、`TurnSkipped`、`PlayerEliminated`
  - 📎 `plan.md` § 待決問題 Q29

#### 實作

- [ ] T075 [US3] 在 `backend/src/rooms/game.ts` 加入回合倒數:每次 `turn.started` 排 `TURN_TIMEOUT_MS`,到期寫入 `outcome: "timeout"` 的紀錄、送 `turn.skipped`、換下一位;斷線不影響倒數(讓 T069 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendTurnSkipped`、`components.schemas.GuessEntry`(`outcome: "timeout"`)
  - 📎 `spec.md` § FR-015
- [ ] T076 [US3] 實作 `backend/src/rooms/sessions.ts`:`onDisconnect(player)` 把 `connection` 設為 `disconnected`、送 `room.updated`,從 `lastSeenAt` 起算 `RESUME_GRACE_MS` 排保留截止(等待中與遊戲中都適用;房主斷線時不轉移房主);`sessionResume(conn, token)` 在保留內取消截止、換上新連線、送 `session.resumed`(`gameViewForSelf()`)與 `room.updated`,不重設任何倒數;座位仍有在線連線時送 `session.replaced` 給舊連線並關閉它;改掉 T039 中「斷線視同離開」的暫時行為(讓 T070、T071 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveSessionResume`、`operations.sendSessionResumed`、`operations.sendSessionReplaced`、`operations.sendRoomUpdated`
  - 📎 `spec.md` § FR-016;`research.md` § R5;`plan.md` § 待決問題 Q8、Q11、Q28
- [ ] T077 [US3] 在 `backend/src/rooms/leave.ts` 加入遊戲中路徑與 `eliminate(room, seat, reason)`:標記出局、重算 `buildTargets()`、送 `player.eliminated`;出局者是目前輪到的人時取消回合倒數並換下一位;在局只剩 1 人時 `endGame(room, seat, "last_player_standing")`;設定階段出局者若已全員設定完則進入猜測;保留截止到期時,遊戲中呼叫 `eliminate(…, "disconnect_timeout")`,等待中走 T039 的離開路徑(讓 T072、T073 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveRoomLeave`、`operations.sendPlayerEliminated`、`operations.sendGameEnded`
  - 📎 `spec.md` § FR-017–FR-019;`plan.md` § 待決問題 Q13
- [ ] T078 [US3] 在 `backend/src/views/player-view.ts` 補上 `sessionResumedFor()`、`turnSkippedFor()`、`playerEliminatedFor()`,在 `backend/src/ws/router.ts` 接上 `session.resume`,在 `backend/src/ws/connection.ts` 的 `close` 改呼叫 `onDisconnect()`(讓 T074 通過)
  - ⚙ `contracts/game.asyncapi.yaml` § `components.schemas.SessionResumed`、`GameViewForSelf`、`TurnState`、`TurnSkipped`、`PlayerEliminated`
  - 📎 `research.md` § R6

### E1 前端(畫面與互動,`frontend/`)

> 可與 E2 平行:先照合約與 `prototype/mock.js` 的假資料把畫面做出來,E2 完成後再接真實訊息

- [ ] T079 [US3] 在 `frontend/src/main.js` 加入重連:連線開啟時若 `sessionStorage` 有 token 就先送 `session.resume`;收到 `RESUME_TOKEN_INVALID` 時清掉 token 回暱稱畫面;連線中斷時自動重連(指數退避,上限 5 秒),重連期間名單與猜測紀錄照常顯示、只把操作區換成「正在重新連線…」;收到 `session.replaced` 時顯示「已在另一個分頁開啟」且不再自動重連
  - ⚙ `prototype/game.html` § `[data-state="reconnecting"]`;`contracts/game.asyncapi.yaml` § `operations.receiveSessionResume`、`operations.sendSessionResumed`、`operations.sendSessionReplaced`
  - 📎 `plan.md` § 待決問題 Q11、Q26;`research.md` § R5
- [ ] T080 [P] [US3] 在 `frontend/src/components/player-list.js` 顯示「斷線中」標示,不顯示剩餘秒數;出局者顯示「N 號已離開」
  - ⚙ `prototype/room.html` § `[data-state="disconnected"]`;`contracts/game.asyncapi.yaml` § `components.schemas.Player`(`connection`)
  - 📎 `plan.md` § 待決問題 Q2、Q20
- [ ] T081 [US3] 在 `frontend/src/pages/game.js` 加入新狀態:收到 `turn.skipped` 在紀錄中顯示「逾時」;收到 `player.eliminated` 更新 `target-ring`;「離開」先跳確認框,寫明「離開就判出局」,確認後送 `room.leave`
  - ⚙ `prototype/game.html` § `[data-state="timeout"]`、`[data-state="disconnected"]`、`[data-state="eliminated"]`、`[data-state="leave-confirm"]`、`#leave-game`;`contracts/game.asyncapi.yaml` § `operations.sendTurnSkipped`、`operations.sendPlayerEliminated`、`operations.receiveRoomLeave`
  - 📎 `spec.md` § FR-015、FR-017;`plan.md` § 待決問題 Q3
- [ ] T082 [US3] 在 `frontend/src/pages/result.js` 加入新狀態;中途離開或出局者只要設定過就公開數字並標「已離開」,沒設定的顯示「沒有設定」
  - ⚙ `prototype/result.html` § `[data-state="last-one"]`、`[data-state="early-end"]`、`#reveal`;`contracts/game.asyncapi.yaml` § `operations.sendGameEnded`(`reason: "last_player_standing"`)
  - 📎 `spec.md` § FR-018;`plan.md` § 待決問題 Q13、Q25

### E3 部署與網路(對外入口,`deploy/`)

- [ ] T083 [US3] 經 `deploy/compose.yaml` 的 nginx 驗證本故事的網路行為:一條連線閒置超過 60 秒(只有 ping/pong)不被 proxy 切斷;關閉分頁或重新整理後經 proxy 重連回原座位;`docker compose restart app` 後前端顯示連線失敗並可重新配對(重啟會清掉對局);結果追加到 `docs/deploy-check.md`
  - ⚙ `deploy/proxy.conf` § `location = /ws`(`proxy_read_timeout 120s`、`proxy_send_timeout 120s`);`deploy/compose.yaml` § `services.app.restart`
  - 📎 `research.md` § R5、§ R11;`plan.md` § 待決問題 Q15、Q19

### 介面覆蓋(US3)

> 必須覆蓋的介面元素(合約的 operation 與 path、DBML 的 Table、原型的每一個狀態、部署檔的 service 與 location)一個都不能少;實作或測試欄空著就是漏了

| 介面元素 | 實作 | 測試 |
|---|---|---|
| `game.asyncapi.yaml` § `operations.receiveSessionResume` | T076、T079 | T070 |
| `game.asyncapi.yaml` § `operations.sendSessionResumed` | T076、T078、T079 | T070、T074 |
| `game.asyncapi.yaml` § `operations.sendSessionReplaced` | T076、T079 | T071、T074 |
| `game.asyncapi.yaml` § `operations.sendTurnSkipped` | T075、T078、T081 | T069、T074 |
| `game.asyncapi.yaml` § `operations.receiveRoomLeave`(遊戲中) | T077、T081 | T072 |
| `game.asyncapi.yaml` § `operations.sendPlayerEliminated` | T077、T078、T081 | T072、T074 |
| `game.asyncapi.yaml` § `operations.sendGameEnded`(`reason: "last_player_standing"`) | T077、T082 | T072、T073 |
| `game.asyncapi.yaml` § `components.schemas.GameViewForSelf`、`TurnState` | T060、T078 | T070、T074 |
| `prototype/game.html` § `[data-state="timeout"]`、`disconnected`、`eliminated`、`leave-confirm` | T081 | T068 |
| `prototype/game.html` § `[data-state="reconnecting"]` | T079 | T068 |
| `prototype/room.html` § `[data-state="disconnected"]` | T080 | T068 |
| `prototype/result.html` § `[data-state="last-one"]`、`early-end` | T082 | T068 |
| `deploy/proxy.conf` § `location = /ws`(閒置逾時) | T009 | T083 |

**Checkpoint**: 三個故事都可獨立運作;T068–T074 全綠,4 人局手動跑一次 Independent Test

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 跨故事的效能、無障礙、部署與文件

- [ ] T084 [P] 撰寫 `scripts/load-test.ts`:400 個 Node 內建 `WebSocket` client 分成 100 間房,開局後依回合送猜測,量測每次操作到同房所有人收到推送的延遲,輸出 p50/p95/p99 與最大房間人數;p95 > 200ms、任一延遲 > 1 秒或任一房間 > 4 人時 exit 1
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.receiveMatchStart`、`operations.receiveGuessSubmit`、`operations.sendGuessResult`
  - 📎 `spec.md` § SC-002、SC-003;`research.md` § R8
- [ ] T085 [P] 撰寫 `scripts/check-bundle-size.ts`:建置後計算 `frontend/dist/**/*.js` 的 gzip 總大小,超過 200KB 時 exit 1
  - 📎 `research.md` § R9
- [ ] T086 [P] 撰寫 `e2e/tests/a11y.spec.ts`:暱稱、房間、對局、結果四個畫面都能只用鍵盤完成主要操作,互動元件有可讀標籤;以 375px 與 1280px 兩種視窗寬度各跑一次 US1 主要路徑
  - ⚙ `prototype/style.css` § `@media (max-width: 600px)`
  - 📎 `spec.md` § NFR-004
- [ ] T087 [P] 撰寫 `e2e/tests/sc001-onboarding.spec.ts`:從開啟網站到看到房間名單,以腳本操作量測耗時並記錄,作為 SC-001(30 秒內)的下限參考;實際的「不看說明」驗收另以真人測試記錄
  - ⚙ `prototype/index.html` § `#match-form`;`prototype/room.html` § `#seat-list`
  - 📎 `spec.md` § SC-001
- [ ] T088 [P] 撰寫 `README.md`(繁體中文):開發(`npm run dev` 前後端各一)、測試指令、時限環境變數、部署(`deploy/`、TLS 交給外層反向代理、重啟會清掉所有對局要挑沒有對局的時段),以及 research「待驗證」三項的驗證方式
  - 📎 `plan.md` § 待決問題 Q14、Q19;`research.md` § 待驗證
- [ ] T089 依 research「待驗證」在部署環境重測:手機切飛航模式後 30 秒內被判斷線(R5)、經反向代理跑 `scripts/load-test.ts`(R8)、反向代理閒置逾時大於 15 秒(R11);結果附在 `docs/deploy-check.md`
  - ⚙ `deploy/proxy.conf` § `location = /ws`
  - 📎 `research.md` § 待驗證、§ R5、§ R8、§ R11

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup(Phase 1)**:沒有依賴,可以立刻開始
- **Foundational(Phase 2)**:依賴 Setup 完成,**擋住所有使用者故事**
- **使用者故事(Phase 3+)**:都依賴 Foundational 完成
- **Polish(Phase 6)**:依賴想交付的故事都完成;T084 需要 US2(要有猜測可以量)

### User Story Dependencies

- **US1(P1)**:Foundational 完成後即可開始,不依賴其他故事
- **US2(P2)**:需要 US1 的房間與配對(`backend/src/rooms/registry.ts`、`matchmaking.ts`、`frontend/src/pages/room.js`);可在 US1 的 E2 任務(T035–T040)完成後就開始 US2 的 E2
- **US3(P3)**:需要 US2 的對局(`backend/src/rooms/game.ts`、`timers.ts`、`views/player-view.ts`);等待中斷線保留(Q8)只需要 US1

### Within Each User Story(依端點)

1. **跨端點驗收**先寫,確認失敗
2. **E2 後端**:測試(先看到失敗)→ `domain/` 純函式 → `rooms/` 用例 → `views/` → `ws/router.ts` 接線
3. **E1 前端**:`components/` → `pages/` → `main.js`;可與 E2 平行,用合約與 `prototype/mock.js` 先做,E2 完成後接真實訊息
4. **E3 部署與網路**:E2、E1 都完成後,經 compose 驗證
5. 跨端點驗收轉綠 → 對過介面覆蓋表,每一列的任務都已完成 → Checkpoint

- 同一個檔案的任務照編號順序做(例如 `backend/src/rooms/game.ts` 的 T056 → T057 → T058 → T059 → T075)

---

## Parallel Example: User Story 1

```bash
# 跨端點驗收與 E2 測試一起寫:
Task: "撰寫 e2e/tests/us1-matchmaking.spec.ts"
Task: "撰寫 backend/test/domain/nickname.test.ts"
Task: "撰寫 backend/test/domain/seats.test.ts"
Task: "撰寫 backend/test/rooms/matchmaking.test.ts"
Task: "撰寫 backend/test/rooms/leave.test.ts"
Task: "撰寫 backend/test/integration/matchmaking-concurrency.test.ts"
Task: "撰寫 backend/test/contract/us1-messages.test.ts"

# E2 與 E1 各一個 agent:
Agent E2: T035 → T036 → T037 → T038 → T039 → T040(backend/)
Agent E1: T041 → T042 → T043 → T044(frontend/)
```

## Parallel Example: User Story 2

```bash
Task: "撰寫 e2e/tests/us2-game.spec.ts"
Task: "撰寫 scripts/verify-score.ts"
Task: "撰寫 backend/test/domain/targets.test.ts"
Task: "撰寫 backend/test/views/no-leak.test.ts"

Agent E2: T054 → T055 → T056 → T057 → T058 → T059 → T060(backend/)
Agent E1: T061、T062、T063 平行 → T064 → T065 → T066 → T067(frontend/)
```

## Parallel Example: User Story 3

```bash
Task: "撰寫 e2e/tests/us3-resilience.spec.ts"
Task: "撰寫 backend/test/rooms/turn-timeout.test.ts"
Task: "撰寫 backend/test/rooms/resume.test.ts"
Task: "撰寫 backend/test/rooms/elimination.test.ts"
Task: "撰寫 backend/test/integration/no-stuck-game.test.ts"

Agent E2: T075 → T076 → T077 → T078(backend/)
Agent E1: T079 → T080 → T081 → T082(frontend/)
之後:T083(deploy/)
```

---

## Implementation Strategy

### MVP First(只做 US1)

1. 完成 Phase 1:Setup
2. 完成 Phase 2:Foundational(擋住所有故事)
3. 完成 Phase 3:US1(含 E3 的 compose 驗證)
4. **停下來驗證**:5 個分頁跑 US1 的 Independent Test,400 人同時配對的整合測試全綠
5. 可以先部署給人試配對

### Incremental Delivery

1. Setup + Foundational → 基礎就緒
2. 加上 US1 → 獨立測試 → 部署(MVP:多人即時連線與配對)
3. 加上 US2 → 獨立測試 → 部署(完整玩一局;此時掛機或斷線還會讓局卡住)
4. 加上 US3 → 獨立測試 → 部署(耐用版,SC-006 成立)
5. Polish:壓測、bundle 大小、無障礙、部署環境重測

---

## Notes

- [P] = 不同檔案、沒有依賴;[Story] 對應 spec.md 的使用者故事;端點節對應 plan.md 端點盤點的 E1/E2/E3
- ⚙ 列的介面元素就是這個任務的完成範圍:做完時逐一對照規格檔裡那個錨點,一個不漏;📎 是判斷細節時的依據
- 介面覆蓋表把合約的 20 個 operations 與其餘 schema、原型的 28 個狀態、部署檔的入口全部分到某個 phase;新增或改動介面元素時,先改覆蓋表再改任務
- 每完成一個任務或一組相關任務就 commit;在任何 Checkpoint 都可以停下來獨立驗證
- 原型提出的五個做法已登記為 plan.md 的 Q23–Q27(T062、T065、T066、T079、T082);房主斷線保留登記為 Q28(T070、T072、T076);合約測試手寫斷言登記為 Q29(T034、T053、T074)
- 避免:模糊的任務、多人同時改同一個檔、會破壞故事獨立性的跨故事依賴
