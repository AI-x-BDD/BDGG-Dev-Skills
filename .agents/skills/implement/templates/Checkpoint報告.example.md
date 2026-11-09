# Checkpoint:Phase 7 User Story 5 - 房內文字聊天 (Priority: P5)

## 任務與 commit

- 任務:70 / 70 已勾選,延後 0;停下的任務:無
- commit:`3f2a9c1` feat(backend): 房內雙方可透過 chat 訊息即時聊天(Refs: T101a、T101b、T102a、T102b、T103a、T103b)
- commit:`8b71e04` feat(backend): 聊天紀錄隨房間保存、重連時回補(Refs: T113a、T113b、T114a、T114b、T115a、T115b)
- commit:`c40d5a2` refactor(backend): 整理聊天的廣播與長度檢查(Refs: T119)
- commit:`e9d1b37` feat(frontend): 房間、對局、結果畫面加上聊天室(Refs: T120a、T120b、T121a、T121b)
- commit:`5d0c8e3` refactor(frontend): 抽出對話泡泡元件(Refs: T136)

## Checkpoint 指令

| 指令 | 結果 |
|---|---|
| `uv run pytest` | exit 0,passed 71 / failed 0 |
| `npx playwright test` | exit 0,passed 34 / failed 0 |
| 重構前後的測試結果 | T119 前後都是 passed 71;T136 前後都是 passed 34;`backend/tests/`、`frontend/e2e/` 的斷言沒有改動 |

## 介面覆蓋表

6 列全勾;測試案例覆蓋表 US5-BE-01~US5-BE-18、US5-AJ-01~US5-AJ-16 全部有紅燈、綠燈與重構

## 未驗證

- 聊天室在手機直向的版面:要用實際手機或瀏覽器的裝置模擬檢查;怎麼驗:開 `http://localhost:5173`,切到 390px 寬,聊天室排在對局區之後、沒有水平捲軸

## 這個 phase 登記的待決問題

- 無

## 要你回答

1. 未驗證的項目照上面的步驟確認過了沒有
2. 沒有要決定的待決問題
3. 可不可以往下做:Phase 8 全域測試區
