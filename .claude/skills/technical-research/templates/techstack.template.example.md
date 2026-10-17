# 技術堆疊:照片相簿整理應用程式

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md) | **Date**: 2026-10-16

## 一覽

| 層 | 技術 | 版本 | 用途 | 決策 |
|---|---|---|---|---|
| 前端 | 原生 HTML / CSS / JS | 不適用 | 介面,不用框架 | R6 |
| 前端 | Custom Elements | 不適用 | 元件,不用 Shadow DOM | R6 |
| 前端 | Vite | 未定 | 開發伺服器與建置 | R6 |
| 前端 | TypeScript(`tsc --noEmit`) | 未定 | 只做 JSDoc 的嚴格型別檢查 | R6 |
| 後端 | Node.js | 22 LTS | 執行環境,原生 type stripping 直接跑 `.ts` | R5 |
| 後端 | TypeScript | 未定 | 後端語言,嚴格模式,不設編譯步驟 | R5 |
| 後端 | Fastify | 5 | HTTP 與請求驗證 | R5 |
| 後端 | `@fastify/static` | 未定 | 提供前端建置產物 | R5 |
| 資料 | MySQL | 8.4 LTS | 照片與相簿的中繼資料 | R4 |
| 資料 | `mysql2` | 未定 | 資料庫驅動,用 promise API,不用 ORM | R4 |
| 領域 | `sharp` | 0.35.5 | JPEG / PNG 縮圖與轉 WebP | R1 |
| 領域 | `heif-thumbnailer` | 1.23(libheif) | HEIC 讀內嵌縮圖 | R1 |
| 領域 | `heif-dec` | 1.23(libheif) | HEIC 解主圖產生預覽 | R1、R9 |
| 領域 | `exiftool-vendored` | 未定 | 讀拍攝時間,需要 `perl` | R3 |
| 測試 | `node:test` | 不適用 | 後端 unit、integration、contract | R11 |
| 測試 | `vitest` | 未定 | 前端 unit | R11 |
| 測試 | `jsdom` | 未定 | `vitest` 的 DOM 環境 | R11 |
| 測試 | `@playwright/test` | 未定 | E2E | R11 |
| 測試 | `@axe-core/playwright` | 未定 | 無障礙檢查 | R11 |
| 測試 | `autocannon` | 未定 | 量 API p95 | R11 |
| 交付 | GitLab CI | 不適用 | lint 到 build 的 pipeline | R12 |
| 交付 | `node:22-trixie-slim` | 22 | image 基底 | R12 |
| 部署 | Unraid Compose Manager | 不適用 | stack 啟停 | R12 |
| 部署 | NPM 存取清單 | 不適用 | 只限內網 | R10 |

## 依賴

- 後端 runtime(5 個):`fastify`(R5)、`@fastify/static`(R5)、`mysql2`(R4)、`sharp`(R1)、`exiftool-vendored`(R3)
- 前端 runtime(0 個):無(R6)
- 開發(9 個):`vite`(R6)、`vitest`(R11)、`jsdom`(R11)、`@playwright/test`(R11)、`@axe-core/playwright`(R11)、`eslint`(R6)、`prettier`(R6)、`typescript`(R6)、`autocannon`(R11)
- 系統套件(apt,4 個):`heif-thumbnailer`(R12)、`libheif-examples`(R12)、`libheif-plugin-libde265`(R12)、`perl`(R12)

## 新引入與沿用

- 新引入:MySQL 8.4 容器,NAS 上第一個 MySQL,和應用程式同一個 compose stack(R4)
- 沿用:GitLab CI 與 Registry(R12)、閘道機上的 NPM(R10)、密碼庫(R12)、Unraid Compose Manager(R12)

## 自寫取代套件

- promise 併發上限器,約 20 行(R2)
- hash router,約 40 行(R6)
- 固定格線的虛擬捲動(R6)
- migration runner(R4)
- 設計 token 檢查 `scripts/check-tokens.mjs`,約 30 行(R6)

## 刻意不用

- React、Lit、htmx:使用者指定不用框架(R6)
- ORM(Prisma、TypeORM):schema 只有 8 張表(R4)
- Express、zod:Fastify 內建 schema 驗證(R5)
- BullMQ + Redis、SSE / WebSocket:單人使用,polling 已足夠(R7)
- `worker_threads`、piscina:HEIC 已在子行程解碼(R2)
- `heic-decode`(wasm)、`exifr`:實測太慢或讀不到 HEIC(R1、R3)
