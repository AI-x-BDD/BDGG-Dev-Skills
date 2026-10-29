# 技術堆疊:線上 1A2B 多人對戰平台

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md) | **Date**: 2026-10-18

## 一覽

| 層 | 技術 | 版本 | 用途 | 決策 |
|---|---|---|---|---|
| 前端 | 原生 HTML / CSS / JS | 不適用 | 3 個畫面,不用框架 | R9 |
| 前端 | 瀏覽器原生 `WebSocket` | 不適用 | 收發房間事件 | R1 |
| 前端 | Vite | 8 | 開發伺服器與建置 | R9 |
| 前端 | TypeScript(`tsc --noEmit --checkJs`) | 未定 | 只做 JSDoc 的嚴格型別檢查 | R9 |
| 後端 | Node.js | 22 LTS | 執行環境,原生 type stripping 直接跑 `.ts` | R2 |
| 後端 | TypeScript | 未定 | 後端語言,嚴格模式,不設編譯步驟 | R2 |
| 後端 | `node:http` | 不適用 | 送前端建置產物、升級 `/ws` | R2 |
| 後端 | `ws` | 8.22.0 | WebSocket 伺服器與 ping/pong 心跳 | R1、R5 |
| 資料 | 行程記憶體 | 不適用 | 房間、玩家與對局狀態,不持久化 | R3 |
| 領域 | `score()` 純函式 | 不適用 | 幾 A 幾 B 計算,前後端共用 | R7 |
| 領域 | `node:crypto` | 不適用 | 重連 token 與逾時代設的祕密數字 | R5、R6 |
| 測試 | `node:test` | 不適用 | 單元與整合測試,`mock.timers` 快轉時鐘 | R4、R10 |
| 測試 | `@playwright/test` | 1.64 | 多 browser context 的端對端測試 | R10 |
| 測試 | 窮舉驗證腳本 | 不適用 | 5,040 × 5,040 組 A/B 比對 | R7 |
| 測試 | 壓測腳本 | 不適用 | 400 位玩家的推送延遲 | R8 |
| 交付 | Docker image(`node:22-slim`) | 22 | 單一 image,同一個 port 送檔案與 WebSocket | R11 |
| 交付 | GitLab CI | 不適用 | lint 到建置的 pipeline | R11 |

## 依賴

- 後端 runtime(1 個):`ws`(R1)
- 前端 runtime(0 個):無(R9)
- 開發(6 個):`vite`(R9)、`typescript`(R2)、`@types/ws`(R2)、`@playwright/test`(R10)、`eslint`(R2)、`prettier`(R2)
- 系統套件(apt,0 個):無(R11)

## 新引入與沿用

- 新引入:WebSocket 長連線服務,環境裡第一個常駐 WebSocket 的應用程式(R1)
- 沿用:GitLab CI 與 Registry(R11)

## 自寫取代套件

- 房間、座位與房主轉移的狀態機,取代 Socket.IO 的 rooms(R1、R3)
- 重連 token 與 60 秒保留,取代 Socket.IO 的自動重連(R5)
- 每位玩家各自的視圖產生函式(R6)

## 刻意不用

- Socket.IO、SSE、輪詢:房間與重連規則仍要自己寫,或延遲與請求量不合適(R1)
- Fastify、Express:後端只送靜態檔與 WebSocket(R2)
- Redis、MySQL、多行程:spec 不持久化,單一行程負載足夠,且會破壞配對的原子性(R3、R8)
- `@sinonjs/fake-timers`:`node:test` 內建 `mock.timers`(R4)
- React、Vue、Svelte、Vitest、jsdom:3 個畫面與純函式邏輯用不到(R9、R10)
