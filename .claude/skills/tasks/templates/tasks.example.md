# Tasks: 線上 PVP 1A2B 猜數字

**Input**: `specs/001-online-guess-number-pvp/` 的設計文件(本 spec package)

**Prerequisites**: plan.md、spec.md、research.md、techstack.md、testplan.md、contracts/game.asyncapi.yaml、contracts/game.dbml、prototype/、deploy/

**Tests**: 依 `testplan.md` 切分。testplan 的每個行為測試案例對應一組 `/tdd` 紅燈與綠燈任務,每個「使用者故事 × 端點」節最後一個 `/tdd` 重構任務;量測與人工驗證的案例對應 📏 任務。

**Organization**: 依 `testplan.md` 的使用者故事分 phase;每個故事底下依 `testplan.md` 的端點分節(E2 後端、E1 前端),外加一節跨端點驗收,最後是介面覆蓋表與測試案例覆蓋表。全域測試區自成一個 phase,放在所有故事之後。

## Format: `[ID] [Story] [步驟] Description`,底下接 🧪、⚙ 與 📎

- **[Story]**:所屬的使用者故事(US1、US2、US3、US4、US5);全域測試區寫 `[G]`
- **[步驟]**:這個任務是 `/implement` 交給誰做的哪一步
  - 🔴 `/tdd 紅燈`:寫一個測試案例的測試,執行確認它失敗
  - 🟢 `/tdd 綠燈`:只寫讓同一個案例通過的程式碼,執行全部測試確認都通過
  - 🔵 `/tdd 重構`:在全部測試綠燈下,整理這一節綠燈任務記下的重構清單,不改行為、不改斷言
  - 📏 量測:照 testplan 案例的條件量測或人工驗證,記下數字與門檻比較;是唯一不對應 `/tdd` 的開發任務
  - 不標步驟的只限三類:工具鏈設定、原樣複製 spec package 的規格檔、CI 設定
- **紅綠成對**:一個 testplan 案例對應同一個三位數的 `a`(🔴)與 `b`(🟢),`b` 依賴 `a`
- **誰做、怎麼排**:同一個 phase 的端點節各交給一個 subagent 平行做;跨端點驗收節在端點節都完成、驗收過後由主 agent 做。每一節裡照任務編號一次做一個任務,做完才做下一個,不跳號
- 每個任務都寫出確切的檔案路徑
- **🧪**:這個任務對應的 `testplan.md` 案例 ID;🔵 寫這一節所有案例的範圍;不標步驟的任務不寫這一行
- **⚙**:這個任務要做出來或測到的介面元素:至少照 `testplan.md` 受測操作表的「規格錨點」欄寫,再加上這個任務實際做出或斷言的介面元素
- **📎**:做這個任務時要對照的依據:`spec.md` § FR / NFR / SC / 邊界情況、`research.md` § R、`plan.md` § Q 或段落名、`techstack.md` § 段落名

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 本例的故事 5 沿用故事 1~4 建好的工具鏈;這裡只示範不標步驟的任務

- [ ] T001 把 spec package 的 `contracts/game.asyncapi.yaml` 原樣複製到 repo 的 `docs/contracts/game.asyncapi.yaml`,內容不改
  - ⚙ `contracts/game.asyncapi.yaml` § 全檔
  - 📎 `plan.md` § Project Structure

---

## Phase 7: User Story 5 - 房內文字聊天 (Priority: P5)

**Goal**: 房內兩位玩家在設定答案、對局中與結果畫面都能即時聊天,紀錄隨房間存續,不影響對局

**Independent Test**: 照 `testplan.md` § 2 的全部案例:E2 後端以 `uv run pytest`、跨端點驗收以 Playwright 兩個 browser context 執行全綠

### E2 後端

- [ ] T101a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-01 的測試(Alice 送 `chat{text:"你好"}`),執行確認它因為「只轉給對手、不回給送出者」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-01
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023、NFR-005
- [ ] T101b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-01 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T101a)
  - 🧪 `testplan.md` § US5-BE-01
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023、NFR-005
- [ ] T102a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-02 的測試(Bob 送 `chat{text:"來一局"}`),執行確認它因為「`sender` 一律填 `host`」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-02
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023
- [ ] T102b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-02 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T102a)
  - 🧪 `testplan.md` § US5-BE-02
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023
- [ ] T103a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-03 的測試(依序送 Alice「一」、Bob「二」、Alice「三」),執行確認它因為「各連線各自排隊,送出者先收到自己的訊息,使兩人看到的順序不同」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-03
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023
- [ ] T103b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-03 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T103a)
  - 🧪 `testplan.md` § US5-BE-03
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023
- [ ] T104a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-04 的測試(Bob 送 `chat{text:"加油"}`),執行確認它因為「對局中只受理 `guess`,把 `chat` 當成不合法的訊息回 `error`」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-04
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023
- [ ] T104b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-04 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T104a)
  - 🧪 `testplan.md` § US5-BE-04
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023
- [ ] T105a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-05 的測試(Alice 送 `chat{text:"再一局?"}`),執行確認它因為「結果階段把房間視為已關閉,拒收 `chat`」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-05
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023
- [ ] T105b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-05 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T105a)
  - 🧪 `testplan.md` § US5-BE-05
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-023
- [ ] T106a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-06 的測試(Alice 送 `chat{text:"有人嗎"}`),執行確認它因為「只有一人時照樣受理並回送 `chat_message`」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-06
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveError`
  - 📎 `spec.md` § FR-025
- [ ] T106b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-06 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T106a)
  - 🧪 `testplan.md` § US5-BE-06
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveError`
  - 📎 `spec.md` § FR-025
- [ ] T107a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-07 的測試(送 `chat{text:"hi"}`),執行確認它因為「未入房的連線送 `chat` 時拋例外斷線,或靜默不回」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-07
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveError`
  - 📎 `spec.md` § FR-025
- [ ] T107b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-07 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T107a)
  - 🧪 `testplan.md` § US5-BE-07
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveError`
  - 📎 `spec.md` § FR-025
- [ ] T108a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-08 的測試(Alice 送 `text` 為 `""`、`"   "`、201 個字元各一次),執行確認它因為「只擋空字串、沒先去除空白」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-08
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveError`
  - 📎 `spec.md` § FR-024
- [ ] T108b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/rules.py` 只寫讓 US5-BE-08 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T108a)
  - 🧪 `testplan.md` § US5-BE-08
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveError`
  - 📎 `spec.md` § FR-024
- [ ] T109a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-09 的測試(Alice 送 200 個字元;再送 `"  你好  "`),執行確認它因為「上限用 `<200` 判斷把 200 字擋掉」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-09
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-024
- [ ] T109b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/rules.py` 只寫讓 US5-BE-09 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T109a)
  - 🧪 `testplan.md` § US5-BE-09
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-024
- [ ] T110a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-10 的測試(Bob 連送 5 則 `chat`;接著 Bob 送 `guess`;Alice 送 `guess`),執行確認它因為「聊天被當成出手而換手」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-10
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-027
- [ ] T110b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-10 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T110a)
  - 🧪 `testplan.md` § US5-BE-10
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § FR-027
- [ ] T111a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-11 的測試(在 T 一半時 Bob 送 `chat`,之後 Alice 不出手),執行確認它因為「聊天把出手計時重置或延後」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-11
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveMatchEnded`
  - 📎 `spec.md` § FR-027
- [ ] T111b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-11 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T111a)
  - 🧪 `testplan.md` § US5-BE-11
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveMatchEnded`
  - 📎 `spec.md` § FR-027
- [ ] T112a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-12 的測試(Alice 送 `chat{text:"在嗎"}`),執行確認它因為「對手斷線時拒收聊天」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-12
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveMatchEnded`
  - 📎 `spec.md` § FR-027、邊界情況
- [ ] T112b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-12 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T112a)
  - 🧪 `testplan.md` § US5-BE-12
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`operations.receiveMatchEnded`
  - 📎 `spec.md` § FR-027、邊界情況
- [ ] T113a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-13 的測試(Alice 送 `chat{text:"我的答案是 1234"}`),執行確認它因為「聊天內容被過濾或遮蔽數字」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-13
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § 邊界情況、NFR-001
- [ ] T113b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-13 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T113a)
  - 🧪 `testplan.md` § US5-BE-13
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § 邊界情況、NFR-001
- [ ] T114a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-14 的測試(Bob 關閉連線,在寬限內以同一個 `client_id` 重新連線),執行確認它因為「聊天紀錄只存在連線物件上,重連後是空的」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-14
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § FR-026
- [ ] T114b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/entities.py`、`backend/src/guess_number/presentation/messages.py` 只寫讓 US5-BE-14 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T114a)
  - 🧪 `testplan.md` § US5-BE-14
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § FR-026
- [ ] T115a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-15 的測試(Alice 送 `chat{text:"在嗎"}`;Bob 在寬限內重連),執行確認它因為「只把訊息推給在線的連線,沒寫進房間的聊天紀錄」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-15
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § FR-026、邊界情況
- [ ] T115b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-15 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T115a)
  - 🧪 `testplan.md` § US5-BE-15
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § FR-026、邊界情況
- [ ] T116a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-16 的測試(雙方送 `play_again` 回到設定答案階段;Alice 再送一則 `chat`),執行確認它因為「再來一局時把聊天紀錄跟著對局一起清掉」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-16
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § FR-026
- [ ] T116b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-16 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T116a)
  - 🧪 `testplan.md` § US5-BE-16
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § FR-026
- [ ] T117a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-17 的測試(Bob 送 `leave`;Carol 與 Dave 先後 `join` 房號 1234),執行確認它因為「聊天紀錄以房號為鍵存放,解散後沒清,同房號新房讀到舊訊息」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-17
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § FR-026、邊界情況
- [ ] T117b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/business/game_service.py`、`backend/src/guess_number/presentation/websocket.py` 只寫讓 US5-BE-17 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T117a)
  - 🧪 `testplan.md` § US5-BE-17
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`、`components.schemas.RoomState`
  - 📎 `spec.md` § FR-026、邊界情況
- [ ] T118a [US5] 🔴 /tdd 紅燈:在 `backend/tests/test_chat.py` 寫 US5-BE-18 的測試(Alice 送 `chat{text:"秘密"}`;Carol 送 `chat{text:"別房"}`),執行確認它因為「聊天廣播給所有連線,而不是只給同房的兩人」這類實作而失敗
  - 🧪 `testplan.md` § US5-BE-18
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § NFR-007
- [ ] T118b [US5] 🟢 /tdd 綠燈:在 `backend/src/guess_number/presentation/connections.py` 只寫讓 US5-BE-18 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T118a)
  - 🧪 `testplan.md` § US5-BE-18
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage`
  - 📎 `spec.md` § NFR-007
- [ ] T119 [US5] 🔵 /tdd 重構:在全部測試綠燈下整理 T101b~T118b 記下的重構清單(範圍限 `backend/src/guess_number/`),每改一小步執行全部測試,變紅就撤回那一步;不改 `backend/tests/` 的斷言(依賴 T118b)
  - 🧪 `testplan.md` § US5-BE-01~US5-BE-18
  - 📎 `testplan.md` § 2.1

### E1 前端

本故事沒有不靠後端的案例(`testplan.md` § 2.2),這一節沒有任務。

### 跨端點驗收(`frontend/e2e/`)

> 端點節都完成、驗收過後由主 agent 開始;真的瀏覽器接真的後端

- [ ] T120a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-01 的測試(Alice 在「訊息」輸入框輸入「你好」並按「送出訊息」),執行確認它因為「送出後沒等伺服器回送就只畫在自己畫面、對手收不到」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-01
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023、NFR-005
- [ ] T120b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-01 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T120a)
  - 🧪 `testplan.md` § US5-AJ-01
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023、NFR-005
- [ ] T121a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-02 的測試(Bob 送出「來一局」,Alice 再送出「好」),執行確認它因為「新訊息插在最前面」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-02
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T121b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-02 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T121a)
  - 🧪 `testplan.md` § US5-AJ-02
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T122a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-03 的測試(Bob 送出「加油」),執行確認它因為「對局畫面沒放聊天室,或放了但沒接上 `chat_message`」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-03
  - ⚙ `prototype/match.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T122b [US5] 🟢 /tdd 綠燈:在 `frontend/src/screens/MatchScreen.jsx`、`frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-03 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T122a)
  - 🧪 `testplan.md` § US5-AJ-03
  - ⚙ `prototype/match.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T123a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-04 的測試(Alice 送出「再一局?」),執行確認它因為「結果畫面沒放聊天室」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-04
  - ⚙ `prototype/result.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T123b [US5] 🟢 /tdd 綠燈:在 `frontend/src/screens/ResultScreen.jsx`、`frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-04 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T123a)
  - 🧪 `testplan.md` § US5-AJ-04
  - ⚙ `prototype/result.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T124a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-05 的測試(觀察房間畫面;接著 Bob 加入,Alice 在輸入框輸入「嗨」),執行確認它因為「等待時仍可送出」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-05
  - ⚙ `prototype/room.html` § `#chat-panel`、`[data-state="chat-waiting"]`
  - 📎 `spec.md` § FR-025
- [ ] T124b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-05 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T124a)
  - 🧪 `testplan.md` § US5-AJ-05
  - ⚙ `prototype/room.html` § `#chat-panel`、`[data-state="chat-waiting"]`
  - 📎 `spec.md` § FR-025
- [ ] T125a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-06 的測試(「訊息」輸入框空白、只有空白字元;再填入 201 個字元並送出),執行確認它因為「只判斷空字串、沒去除空白」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-06
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-024
- [ ] T125b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-06 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T125a)
  - 🧪 `testplan.md` § US5-AJ-06
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-024
- [ ] T126a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-07 的測試(Alice 送出 `<b>粗</b><script>window.__x=1</script>`),執行確認它因為「為了泡泡排版改用 `dangerouslySetInnerHTML` 畫訊息內容」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-07
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § NFR-008
- [ ] T126b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-07 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T126a)
  - 🧪 `testplan.md` § US5-AJ-07
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § NFR-008
- [ ] T127a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-08 的測試(Bob 重新整理頁面),執行確認它因為「聊天紀錄只存在前端記憶體,重新整理後沒從 `room_state.chat` 還原」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-08
  - ⚙ `prototype/match.html` § `#chat-panel`
  - 📎 `spec.md` § FR-026
- [ ] T127b [US5] 🟢 /tdd 綠燈:在 `frontend/src/game/gameClient.js` 只寫讓 US5-AJ-08 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T127a)
  - 🧪 `testplan.md` § US5-AJ-08
  - ⚙ `prototype/match.html` § `#chat-panel`
  - 📎 `spec.md` § FR-026
- [ ] T128a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-09 的測試(雙方按「再來一局」回到房間畫面;Bob 送出「再戰」),執行確認它因為「前端在再來一局時把聊天 state 跟對局一起清掉」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-09
  - ⚙ `prototype/result.html` § `#chat-panel`;`prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-026
- [ ] T128b [US5] 🟢 /tdd 綠燈:在 `frontend/src/game/gameClient.js` 只寫讓 US5-AJ-09 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T128a)
  - 🧪 `testplan.md` § US5-AJ-09
  - ⚙ `prototype/result.html` § `#chat-panel`;`prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-026
- [ ] T129a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-10 的測試(Bob 送出「快點」),執行確認它因為「前端收到聊天時重算或重設倒數,使倒數跳回 7~8 秒」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-10
  - ⚙ `prototype/match.html` § `#chat-panel`、`#guess-form`
  - 📎 `spec.md` § FR-027
- [ ] T129b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/Countdown.jsx` 只寫讓 US5-AJ-10 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T129a)
  - 🧪 `testplan.md` § US5-AJ-10
  - ⚙ `prototype/match.html` § `#chat-panel`、`#guess-form`
  - 📎 `spec.md` § FR-027
- [ ] T130a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-11 的測試(Alice 送出「在嗎」;Bob 在寬限內用同一個瀏覽器重新開啟網址),執行確認它因為「等待重連時停用聊天輸入」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-11
  - ⚙ `prototype/match.html` § `#chat-panel`
  - 📎 `spec.md` § FR-026、邊界情況
- [ ] T130b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-11 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T130a)
  - 🧪 `testplan.md` § US5-AJ-11
  - ⚙ `prototype/match.html` § `#chat-panel`
  - 📎 `spec.md` § FR-026、邊界情況
- [ ] T131a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-12 的測試(Bob 離開房間,Alice 回到首頁;Carol 與 Dave 用同一組房號進房),執行確認它因為「前端沿用上一間房的聊天 state」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-12
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-026、邊界情況
- [ ] T131b [US5] 🟢 /tdd 綠燈:在 `frontend/src/game/gameClient.js` 只寫讓 US5-AJ-12 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T131a)
  - 🧪 `testplan.md` § US5-AJ-12
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-026、邊界情況
- [ ] T132a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-13 的測試(1234 房的 Alice 送出「暗號」),執行確認它因為「聊天廣播給所有連線」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-13
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § NFR-007
- [ ] T132b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-13 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T132a)
  - 🧪 `testplan.md` § US5-AJ-13
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § NFR-007
- [ ] T133a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-14 的測試(Alice 送出「你好」,Bob 送出「嗨」),執行確認它因為「不分自己與對手,泡泡一律靠同一側」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-14
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T133b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-14 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T133a)
  - 🧪 `testplan.md` § US5-AJ-14
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T134a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-15 的測試(房主送出「我是房主」,挑戰者送出「我是挑戰者」),執行確認它因為「用暱稱判斷是不是自己的訊息,同暱稱時雙方的泡泡全部靠右」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-15
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023、邊界情況
- [ ] T134b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-15 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T134a)
  - 🧪 `testplan.md` § US5-AJ-15
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023、邊界情況
- [ ] T135a [US5] 🔴 /tdd 紅燈:在 `frontend/e2e/chat.spec.js` 寫 US5-AJ-16 的測試(Alice 連續送出「第1則」到「第20則」),執行確認它因為「聊天室沒有高度上限,訊息越多把頁面撐越長」這類實作而失敗
  - 🧪 `testplan.md` § US5-AJ-16
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T135b [US5] 🟢 /tdd 綠燈:在 `frontend/src/components/ChatPanel.jsx` 只寫讓 US5-AJ-16 通過的程式碼,執行全部測試確認都通過;看到要整理的地方記進重構清單(依賴 T135a)
  - 🧪 `testplan.md` § US5-AJ-16
  - ⚙ `prototype/room.html` § `#chat-panel`
  - 📎 `spec.md` § FR-023
- [ ] T136 [US5] 🔵 /tdd 重構:在全部測試綠燈下整理 T120b~T135b 記下的重構清單(範圍限 `frontend/src/`),每改一小步執行全部測試,變紅就撤回那一步;不改 `frontend/e2e/` 的斷言(依賴 T135b)
  - 🧪 `testplan.md` § US5-AJ-01~US5-AJ-16
  - 📎 `testplan.md` § 2.3

### 介面覆蓋(US5)

| 介面元素 | 綠燈 | 紅燈 |
|---|---|---|
| `game.asyncapi.yaml` § `operations.sendChat`、`operations.receiveChatMessage`、`components.schemas.ChatMessage` | T101b~T118b | T101a~T118a |
| `game.asyncapi.yaml` § `components.schemas.RoomState`(`chat` 欄位) | T113b~T117b | T113a~T117a |
| `game.asyncapi.yaml` § `operations.receiveError` | T106b~T108b | T106a~T108a |
| `prototype/room.html` § `#chat-panel`、`[data-state="chat-waiting"]` | T120b、T124b | T120a、T124a |
| `prototype/match.html` § `#chat-panel` | T122b | T122a |
| `prototype/result.html` § `#chat-panel` | T123b | T123a |

### 測試案例覆蓋(US5)

> `testplan.md` 本故事的每個案例都要有一組紅綠任務;每個有案例的節都要有一個重構任務

| testplan 案例 | 紅燈 | 綠燈 | 重構 |
|---|---|---|---|
| US5-BE-01~US5-BE-18 | T101a~T118a | T101b~T118b | T119 |
| US5-AJ-01~US5-AJ-16 | T120a~T135a | T120b~T135b | T136 |

**Checkpoint**: `uv run pytest`、`npx playwright test` 全綠;重構任務前後的測試結果相同

---

## Phase 8: 全域測試區

**Purpose**: 照 `testplan.md` § 3.2 驗證適用到範疇內故事的全域 NFR 與 SC

- [ ] T139 [G] 📏 量測:撰寫 `scripts/load_test.py`,照 G-01 開 50 間房、每房每 2 秒一次 `guess`、每 5 秒一則 `chat`,持續 5 分鐘;輸出 `guess_result` 與 `chat_message` 的 p95 延遲,和門檻(p95 ≤ 1 秒)比較,結果寫進 `specs/001-online-guess-number-pvp/measurements.md`
  - 🧪 `testplan.md` § G-01
  - ⚙ `contracts/game.asyncapi.yaml` § `operations.sendGuess`、`operations.receiveGuessResult`、`operations.sendChat`
  - 📎 `spec.md` § NFR-005、SC-003

### 測試案例覆蓋(全域)

| testplan 案例 | 任務 |
|---|---|
| G-01 | T139 |

**Checkpoint**: 全部測試綠燈;`measurements.md` 每一項都寫了數字與是否過門檻,沒過的列為待決問題
