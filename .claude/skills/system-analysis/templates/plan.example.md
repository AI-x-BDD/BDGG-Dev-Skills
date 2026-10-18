# 系統分析規劃: 照片相簿整理應用程式

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md) | **Techstack**: [techstack.md](./techstack.md) | **Date**: 2026-10-18

## Project Structure

### Documentation (this feature)

```text
specs/001-photo-album-organizer/
├── spec.md              # 輸入(specify 產出)
├── research.md          # 輸入(technical-research 產出)
├── techstack.md         # 輸入(technical-research 產出)
├── plan.md              # 本文件
├── data-model.md        # S4 產出(E3 資料庫)
└── contracts/
    ├── payment.md       # S1 產出(E7 第三方金流)
    ├── ui.md            # S2 產出(E1 前端)
    ├── openapi.yaml     # S3 產出(E2 後端 REST API)
    ├── filesystem.md    # S5 產出(E4 檔案系統)
    ├── imaging.md       # S6 產出(E5 影像處理工具)
    ├── metadata.md      # S7 產出(E8 拍攝資訊讀取工具)
    └── deploy.md        # S8 產出(E6 部署與網路)
```

### Source Code (repository root)

```text
package.json                 # npm workspaces: backend, frontend, e2e
.gitlab-ci.yml

backend/
├── src/
│   ├── routes/              # E2 後端 REST API
│   ├── services/            # 用例;匯入與重新掃描讀寫 E4 檔案系統
│   ├── payment/             # E7 第三方金流的串接
│   ├── repos/               # E3 資料庫的存取
│   ├── db/                  # E3 資料庫的連線與 migration
│   ├── imaging/             # E5 影像處理工具的呼叫
│   ├── metadata/            # E8 拍攝資訊讀取工具的呼叫
│   └── domain/              # 不依賴 I/O 的純函式
└── test/

frontend/
├── src/
│   ├── pages/               # E1 前端畫面
│   └── components/          # E1 前端可重用的互動
└── test/

e2e/                         # 跨端點的端對端測試

deploy/                      # E6 部署與網路
```

**Structure Decision**: 前後端分成兩個 workspace,但打包成**同一個 image**:Fastify 同時提供 `/api` 和前端的建置產物。好處是同源,不用處理 CORS,NPM 也只要一個 proxy host。MySQL 是同一個 stack 裡的第二個 service。

後端分層是 `routes → services → (repos → db | payment | imaging | metadata)`:`services/` 是用例,往下呼叫四種對外部的轉接——`repos/` 接資料庫、`payment/` 接金流商、`imaging/` 接影像處理工具、`metadata/` 接拍攝資訊讀取工具。`domain` 是不依賴 I/O 的純函式,讓核心邏輯可以用 < 100ms 的單元測試涵蓋。

前端照畫面分 `pages/`,可重用的互動放在 `components/`(Custom Elements)。

## 分析流程規劃

> 本段只排定分析的順序,**還不做分析**。每個介面在後續各占至少一個步驟,分析結果由那一步產出。

### 端點盤點

這次需求涉及 8 個端點。每個端點視為一個獨立系統,分析的對象是它對外的介面:

| # | 端點 | 介面 | 需求出處 |
|---|---|---|---|
| E1 | 前端(瀏覽器) | 畫面與互動:頁面、狀態、鍵盤操作、詞彙 | FR-012、FR-013、FR-014、SC-001、SC-003 |
| E2 | 後端(Fastify) | REST API:資源、操作、錯誤碼、長時間工作的進度與取消 | FR-001–FR-011、FR-013、FR-017 |
| E3 | 資料庫(MySQL) | 資料表、關聯、唯一性與狀態約束 | FR-004、FR-009、FR-010、FR-016、Key Entities |
| E4 | 檔案系統 | 照片原檔(`PHOTO_ROOT` 唯讀)與縮圖(`DATA_DIR`)的路徑與讀寫規約 | FR-001、FR-005、FR-017、SC-006 |
| E5 | 影像處理工具(libheif CLI、sharp) | 外部程序呼叫:輸入格式、參數、輸出、逾時與失敗原因 | FR-011、SC-002、Assumptions(JPEG/PNG/HEIC) |
| E6 | 部署與網路(Docker、NPM 反向代理) | 對外入口:port、掛載、HTTPS、付款通知的回呼路徑 | FR-018、Assumptions(自架於家中伺服器) |
| E7 | 第三方金流(如綠界 ECPay) | 金流商 API:建立交易、付款頁導轉、付款結果通知(webhook)、簽章驗證、查單 | FR-018 |
| E8 | 拍攝資訊讀取工具(ExifTool) | 外部程序呼叫:讀取的欄位、時間的原始格式、缺失時的回傳、失敗原因 | FR-006、FR-007、SC-004 |

### 分析波段

排序原則:**一個介面排在它所依賴的介面都分析完之後**;同一波裡的介面彼此不依賴,可以各開一個 sub agent 平行分析。

第三方端點的介面是對方定好的,我們只能照著接、不能改,所以它不依賴我們任何一個介面;
反過來,我們這邊碰到它的介面都要遷就它。因此**第三方端點排在最前面**,依賴它的介面往後推一波。

| Wave | 步驟 | 介面 | 平行 | 排在這一波的理由 |
|---|---|---|---|---|
| 1 | S1 | E7 第三方金流 | — | 金流商的介面已經定好,不依賴任何介面;前端的付款導轉與後端的建單、收通知都要照它設計 |
| 2 | S2 | E1 前端畫面與互動 | ✅ 與 S3 平行 | 由使用者故事推出;結帳、導向付款頁與付款完成頁的流程要照 S1 的導轉方式 |
| 2 | S3 | E2 後端 REST API | ✅ 與 S2 平行 | 由 FR 推出;建立訂單、接收付款通知的端點要照 S1 的參數與簽章。前端與後端以同一份需求為準,不必等對方 |
| 3 | S4 | E3 資料庫 | ✅ 與 S5、S6、S7 平行 | 要存什麼由 S3 的資源與操作決定(含訂單與付款狀態) |
| 3 | S5 | E4 檔案系統 | ✅ 與 S4、S6、S7 平行 | 要讀哪些原檔、寫哪些縮圖由 S3 的匯入與重新掃描決定 |
| 3 | S6 | E5 影像處理工具 | ✅ 與 S4、S5、S7 平行 | 要產出哪些縮圖、失敗要回報什麼由 S3 決定 |
| 3 | S7 | E8 拍攝資訊讀取工具 | ✅ 與 S4、S5、S6 平行 | 要讀哪些拍攝資訊、缺失時要回報什麼由 S3 的匯入與自動分類決定 |
| 4 | S8 | E6 部署與網路 | — | 要開哪些 port、掛哪些路徑、DB 放哪個網路,要等 S3–S7 都定下來;S1 的付款通知要打到哪一條回呼路徑,也在這一步定 |

共 4 個 wave、8 個步驟:Wave 1 一個介面,Wave 2 兩個介面平行,Wave 3 四個介面平行,Wave 4 一個介面。
