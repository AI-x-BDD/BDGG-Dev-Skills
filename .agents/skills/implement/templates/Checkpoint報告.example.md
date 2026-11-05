# Checkpoint:Phase 2 Foundational (Blocking Prerequisites)

## 任務與 commit

- 任務:18 / 18 已勾選,延後 0;停下的任務:無
- commit:`3f2a9c1` feat(shared): 新增祕密數字的格式檢查與分數計算(Refs: T010、T011、T013、T014)
- commit:`8b71e04` feat(shared): 依合約定義協定型別(Refs: T015)
- commit:`c40d5a2` feat(backend): 實作訊息檢查、推送與連線層(Refs: T012、T016、T017、T018、T019、T020、T021、T022)
- commit:`e9d1b37` feat(frontend): 建立前端外殼與連線模組(Refs: T023、T024、T025、T026、T027)

## Checkpoint 指令

| 指令 | 結果 |
|---|---|
| `npm run lint` | exit 0,0 個警告 |
| `npm run typecheck` | exit 0 |
| `npm test` | exit 0,tests 31 / pass 31 / fail 0 |
| `node backend/src/server.ts` | 能送出前端外殼;`/ws` 升級成功;15 秒心跳實測收到 2 次 ping |

## 介面覆蓋表

8 列中 2 列全勾;`operations.sendError`(等 T034,Phase 3)、`channels.game`(等 T070,Phase 5)、`prototype/style.css` § `:root`(等 T086,Phase 6)等 6 列等後面的 phase

## 未驗證

- 前端外殼在手機寬度的版面:要用實際手機或瀏覽器的裝置模擬檢查;怎麼驗:開 `http://localhost:8080`,切到 375px 寬,標題與連線狀態列不換行、不溢出

## 這個 phase 登記的待決問題

- 無

## 要你回答

1. 未驗證的項目照上面的步驟確認過了沒有
2. 沒有要決定的待決問題
3. 可不可以往下做:Phase 3 User Story 1 - 輸入暱稱並自動配對進房
