# Phase 0 Research: 照片相簿整理應用程式

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-16

使用者指定的技術方向:

- 前端:Vite + 原生 HTML / CSS / JS,套件數量最少,不用 React。
- 後端:Node.js。
- 資料庫:MySQL。

每個「理由」都標出證據類型:**實測**(附量測環境)、**估算**(附依據)、**查證**(附來源)、**判斷**(推論)。探針腳本放在 session 暫存區,不進 repo。對應的效能驗收是 [quickstart.md](./quickstart.md) 的 V-PERF,要在 NAS 上用真實照片重測。

---

## R1. HEIC 解碼(FR-001、SC-002)

**決策**:

- **HEIC 縮圖**:用 Debian trixie 原生的 `heif-thumbnailer -s 256`(libheif 1.23 + libde265)。有內嵌縮圖就直接解它;沒有的話,這支工具會**自動備援**為解碼主圖,不需要自己寫分支。它的 PNG 輸出寫到 `/data/tmp`,再交給 `sharp` 轉成 256px WebP。
- **小縮圖的備援**:內嵌縮圖的長邊小於 256px 時(相機廠商不一定),改帶 `-p` 從主圖重新產生,避免放大後變糊。
- **HEIC 預覽(1600px)**:用同一套 libheif 的 `heif-dec` 把主圖解碼後交給 sharp(R9)。
- **JPEG / PNG**:直接用 `sharp`。
- 記錄每張縮圖的來源 `thumb_source`(`embedded` 或 `decoded`),讓 V-PERF-1 能看出真實照片庫的命中率。

**理由**:

- 判斷:HEIC 能不能解碼,決定匯入管線能不能做。
- 實測(桌機 i5-9400F,Docker,12MP 雜訊圖。雜訊最難壓縮,所以「完整解碼」的數字是最壞情況):

| 方案 | 結果 |
|---|---|
| `sharp` 0.35.5 預建版本直接讀 HEIC | ❌ `bad seek`。`sharp.format.heif.input.fileSuffix` 只有 `[".avif"]`,預建的 libvips 沒有 HEVC 解碼器 |
| `heic-decode`(wasm)+ `sharp`,完整解碼 | ✅ 每張 1.55–1.69 秒 |
| 原生 `heif-convert`(bookworm,libheif 1.15),完整解碼 | ✅ 每張 1.49–1.52 秒 |
| **`heif-thumbnailer`(trixie,libheif 1.23.4),有 320×240 內嵌縮圖** | ✅ **每張 26–27ms**,含行程啟動與 PNG 輸出 |
| `heif-thumbnailer`,沒有內嵌縮圖,自動備援 | ✅ 每張 1.22–1.31 秒 |
| JPEG 走 `sharp`(會自動 shrink-on-load) | ✅ 每張 0.089 秒 |

- 判斷:有內嵌縮圖時約快 **47 倍**。手機拍的 HEIC 通常都有內嵌縮圖,所以匯入時間主要由「沒有內嵌縮圖的比例」決定,要在 V-PERF-1 用真實照片量出來。
- 實測(同一個 HEIC 檔,原生 libheif 1.23.4 對照 `libheif-js` 1.23.5),說明為什麼不用 wasm 讀內嵌縮圖:`libheif-js` 雖然匯出了 `heif_image_handle_get_number_of_thumbnails` 等函式,但**原生 `heif-info` 回報 `thumbnail: 320x240`,libheif-js 卻回傳 0**。它的 handle 是 embind 物件,不是原生指標,也沒辦法改呼叫 `_` 開頭的 C 函式繞過去。跟一個綁定不完整的套件硬碰,不如直接用原生工具。
- 查證(`pillow-heif` 1.x changelog):`pillow-heif` 1.x 已經拿掉縮圖 API,Python 這條路也走不通。
- 判斷:連帶的簡化是不再需要 `heic-decode`,也不需要 `worker_threads` 池(R2)。

**考慮過的替代方案**:

- `heic-decode`(wasm)完整解碼:每張都要約 1.6 秒,而且無法利用內嵌縮圖。
- 自己解析 ISOBMFF,把縮圖 item 拆出來另外解碼:等於重寫一部分 libheif,不值得。
- 讓 sharp 改連系統的 libvips(搭配 libheif):要從原始碼編譯 sharp,而且 libvips 的 heifload不一定會選用內嵌縮圖。

## R2. 匯入吞吐量(SC-002)

**決策**: 用一個 promise 併發上限器(約 20 行,不加套件)控制「同時處理幾張照片」。預設值是 `min(os.availableParallelism() - 2, 8)`,可用環境變數 `IMAGE_CONCURRENCY` 覆寫。

- HEIC 由 `heif-thumbnailer` 和 `heif-dec` 在**子行程**中解碼,天生不占 Node 主執行緒。
- `sharp` 本身就在 libuv threadpool 中執行(`UV_THREADPOOL_SIZE` 設成和併發上限一致)。
- 資料庫寫入集中在主執行緒,用單一連線依序執行。

**理由**:

- 估算(R1 的每張實測時間 × 1,000 張 ÷ 併發數):

| 情況 | 單一併發 | 8 個併發(NAS i5-13500,20 執行緒) |
|---|---|---|
| 1,000 張 HEIC 都有內嵌縮圖 | 約 27 秒(+ 雜湊與 EXIF) | 遠低於預算 |
| 1,000 張 HEIC 都沒有內嵌縮圖(最壞情況) | 約 1,300 秒 | 約 165 秒,< 300 秒預算 |

- 判斷:這只是估計,仍然**必須在 NAS 用真實照片實測**(V-PERF-1)。
- 估算(12MP × 4 bytes/像素):沒有內嵌縮圖時,每個子行程解一張 12MP 圖約 50MB,8 個併發合計約 400MB。
- 判斷:併發數量就是記憶體上限,記憶體用量不隨輸入規模增加。

**考慮過的替代方案**: `worker_threads` 池(解碼已經在子行程中進行,不需要再多一層)、piscina(同前)。

## R3. 讀取拍攝時間 EXIF(FR-008、FR-010、SC-004)

**決策**: 用 `exiftool-vendored`(背後是常駐的 ExifTool 行程,Docker image 需要 `perl`)。讀 `DateTimeOriginal` 的 **rawValue 原始字串**;沒有的話退到 `CreateDate`,再沒有就視為缺失。**不**從檔名或修改時間推測(spec 的「假設」)。

**理由**:

- 實測(同一組 JPEG 與 HEIC 樣本,`DateTimeOriginal` 為 `2026:10:05 14:30:00`):

| 函式庫 | JPEG | HEIC |
|---|---|---|
| `exifr` 7.x 預設 | 讀得到,但回傳 `2026-10-05T14:30:00.000Z`:**把沒有時區的本地時間當成 UTC** | ❌ `Malformed EXIF data` |
| `exifr` 加 `reviveValues:false` | `2026:10:05 14:30:00` ✅ | ❌ 同上 |
| `exiftool-vendored` | rawValue `2026:10:05 14:30:00`,沒有加時區 ✅ | 同 JPEG ✅,平均每張 14ms |

- 判斷:同一個 HEIC,ExifTool 讀得出來而 exifr 讀不出來,問題在 exifr,不在樣本。
- 判斷:另一個陷阱是 exifr 預設會把無時區時間轉成 UTC。容器的時區是 UTC,台灣晚上 8 點以後拍的照片換成 UTC 會落到前一天;如果剛好是某月 1 日,就會被分到上個月。這直接違反 SC-004,因此規定:**拍攝時間一律以「牆上時間」字串處理,全程不轉時區**。

**考慮過的替代方案**: exifr(上面兩個問題)、sharp 的 `metadata().exif`(sharp 打不開 HEIC)。

## R4. 資料庫:MySQL 的部署與 schema 陷阱(使用者指定、FR-014、NFR-006)

**決策**: 新建 **MySQL 8.4 LTS** 容器。它和應用程式放在同一個 compose stack 的內部網路,**不對 host 開 port**。資料目錄放在 `/srv/appdata/photo-albums/mysql`。驅動用 `mysql2/promise`,不用 ORM;migration 是編號的 `.sql` 檔,由自寫的小 runner 執行。

**理由**:

- 實測(NAS `list_containers`):沒有現成的 MySQL/MariaDB,只有 其他服務專用的 Postgres,共用無從談起。建在同一個 stack 裡,和現有的 其他自架服務 是同一個模式。
- 估算(10,000 張 × 每張數百 bytes 的中繼資料):資料量是 MB 等級,不需要調校。
- 查證(MySQL 8.4 Reference Manual、mysql2 文件):有四個會影響正確性的陷阱,這次一次寫進設計:

1. **名稱唯一性不能交給 collation**。MySQL 8.4 預設的 `utf8mb4_0900_ai_ci` 不分大小寫,但**也不分重音**(`é` = `e`),比 FR-014「只忽略英文大小寫」寬。做法:應用程式自行算出 `name_key`(trim 後只把 A–Z 轉小寫),存進 collation 為`utf8mb4_0900_bin` 的欄位並建 UNIQUE。`0900_bin` 是 NO PAD,`'a'` 和 `'a '` 不會被當成相同。
2. **DATETIME 的時區轉換**。mysql2 預設會把 `DATETIME` 轉成 JS `Date`(套用行程時區),和 R3 是同一類陷阱。連線池設 `dateStrings: true`,拍攝時間全程用字串。
3. **長路徑做不了唯一索引**。utf8mb4 的 `VARCHAR(1024)` 超過 InnoDB 3072 bytes 的索引上限。改用 `path_hash BINARY(32)`(sha256 of `folder_id + '\0' + rel_path`)建 UNIQUE。
4. **NULL 排序**。MySQL 的 ASC 排序會把 NULL 排最前面,但沒有拍攝時間的照片應該排最後。用 STORED 生成欄位 `sort_at = COALESCE(taken_at, '9999-12-31 23:59:59')` 搭配索引 `(sort_at, id)`做 keyset 分頁。

**考慮過的替代方案**: SQLite(更簡單,但使用者指定 MySQL)、MariaDB(和 MySQL 8 的`0900` collation 與生成欄位行為有差異,沒有理由偏離使用者指定的 MySQL)、ORM(Prisma 或 TypeORM會增加依賴和抽象,而 schema 只有 8 張表)。

## R5. 後端框架與語言(使用者指定、憲法〈語言寫出型別檢查方式〉)

**決策**: **Node.js 22 LTS + TypeScript(嚴格模式),用 Node 原生的 type stripping 直接執行,不另設編譯步驟**。HTTP 用 **Fastify 5**,搭配 `@fastify/static` 提供前端的建置產物。請求驗證用 Fastify 內建的 JSON Schema(ajv),不另加 zod。

**理由**:

- 判斷:憲法 `constitution/technical-research/techstack.md`〈語言寫出型別檢查方式〉要求 techstack 的語言一列寫出型別檢查方式;TypeScript 開 `strict` 就寫得出來。
- 查證(Node.js 22.18.0 release notes):Node 22.18 以後 type stripping 預設開啟。
- 實測(桌機 Node v22.23.2):`.ts` 檔直接執行成功。所以可以用 TS 寫,但不需要 tsc 輸出或 bundler,只在 CI 跑`tsc --noEmit` 做檢查。tsconfig 開 `erasableSyntaxOnly`,禁止 enum、namespace 這類需要轉譯的語法。
- 判斷:Fastify 的 route schema 同時用在驗證和回應序列化,可以直接對照 contracts/openapi.yaml 做合約測試。

**考慮過的替代方案**: Express(沒有內建 schema 驗證,要自己補)、原生 `node:http`(路由、驗證、靜態檔都要自己寫,反而比較複雜)、後端也寫原生 JS(型別檢查要另外補)。

## R6. 前端:原生 HTML / CSS / JS 的最小構成(使用者指定、NFR-001、NFR-004、憲法〈語言寫出型別檢查方式〉)

**決策**:

- **runtime 依賴:0 個**。只有開發依賴:`vite`、`vitest` + `jsdom`、`@playwright/test` + `@axe-core/playwright`、`eslint` + `prettier`、`typescript`(只用來做型別檢查)。
- **型別**:原生 `.js` 加 JSDoc 註記,`jsconfig.json` 開 `checkJs` + `strict`,用 `tsc --noEmit` 檢查。寫的仍然是瀏覽器直接能跑的 JS,型別檢查方式是 `tsc --noEmit`。
- **元件**:原生 Custom Elements,**不用 Shadow DOM**,讓設計 token 和全域樣式直接生效,無障礙樹也比較單純。
- **路由**:自寫 hash router(`#/albums/12`),約 40 行。
- **大量縮圖**:自寫固定格線的虛擬捲動。所有縮圖格子同樣大小,只需算出「可見列範圍」;DOM 節點數量只跟視窗大小有關,不受照片總數影響。
- **i18n**:`src/i18n/zh-TW.json` 搭配一個 `t(key, params)` 函式(介面文字集中管理)。
- **設計 token**:`styles/tokens.css` 定義 CSS custom properties,其他 CSS 和 JS 只能引用 `var(--…)`。強制方式不加 stylelint,改用一支約 30 行的 `scripts/check-tokens.mjs`(Node 原生,不需套件)。它掃描 `tokens.css` 以外的檔案,發現色碼、`rgb()` 或非 0 的 `px` 字面值就讓 CI 失敗。這支檢查器要附一個**故意違規的對照樣本**,證明它真的抓得到。
- **對話框**:原生 `<dialog>`,內建 focus trap 和 Esc 關閉,用於刪除確認(破壞性操作要確認)。

**理由**:

- 判斷:依使用者要求「簡單一點」,runtime 依賴維持 0 個。
- 估算(router 約 40 行、虛擬捲動與元件都是自寫的小模組,沒有框架):JS 建置產物 gzip 後遠小於 30KB,體積不構成問題。

**考慮過的替代方案**: Lit(很小,但仍是框架)、htmx(要伺服器端 render 片段,虛擬捲動也不好做)、虛擬捲動套件(格子固定大小時自寫很簡單)。

## R7. 長時間工作:進度、取消、中斷復原(NFR-003、邊界情況「中斷」)

**決策**:

- 匯入、重新掃描、自動分類都是一個 **job**,狀態持久化在 MySQL 的 `jobs` 表。在應用程式行程內執行,同一時間最多一個 job 在跑,多送的排隊。
- **進度**:前端每 500ms polling `GET /api/jobs/{id}`。不用 SSE,因為 NPM 反向代理加 SSE 要額外處理 buffering。
- **取消**:`POST /api/jobs/{id}/cancel` 設置旗標;job 每處理完一張照片就檢查一次。
- **一張一個交易**:每張照片的「寫入 photo 列 + 計數器 +1」在同一個交易內完成。縮圖先寫進暫存檔,完成後 `rename` 成正式檔(原子操作)。中斷時最多丟掉正在處理的那一張。
- **重啟復原**:啟動時把 `running` / `cancelling` 的 job 標成 `interrupted`。使用者重新執行時,已匯入的照片會因 sha256 重複而跳過,所以重跑是冪等的。
- **套用分類建議**:整批在**一個交易**內完成,要嘛全部套用,要嘛全部不套用,不會只套一半。

**理由**:

- 判斷:單人使用,同一時間只有一個 job,行程內執行加上 MySQL 持久化就夠了,不需要另一套佇列服務。
- 判斷:進度用 polling,是因為 NPM 反向代理加 SSE 要額外處理 buffering。
- 判斷:「一張一個交易」加上縮圖的原子 `rename`,讓中斷的損失有上限(最多一張);再加上 R8 的 sha256 去重,重跑不會產生重複資料,中斷復原不需要另寫補償邏輯。

**考慮過的替代方案**: 外部佇列(BullMQ + Redis,單人使用不需要)、SSE / WebSocket(polling 已足夠)。

## R8. 重複辨識與重新掃描(FR-002、FR-004)

**決策**:

- 指紋是**整個檔案內容的 sha256**,存成 `BINARY(32)` 並建 UNIQUE。依 spec,不同解析度或編輯過的版本視為不同照片。
- 同一份內容出現在兩個路徑時,只建一筆 photo,另一個路徑記為「重複,略過」。
- **重新掃描**的步驟:
  1. 走訪資料夾。檔案的 `(size, mtime)` 和上次相同就不重算雜湊(效能)。
  2. 新的路徑:算雜湊後比對。
     - 雜湊不存在 → 新增照片。
     - 雜湊屬於一張「找不到原檔」的照片 → **重新連結**到新路徑,並清除該標記。這涵蓋使用者在系統外搬動檔案的情況,相簿歸屬也會保留。
  3. 原有的路徑已不存在 → 設定 `file_missing = 1`,保留相簿歸屬,不刪除紀錄。
- **不**背景監看、不排程(FR-004)。

**理由**:

- 判斷:spec 的「假設」規定不同解析度或編輯過的版本視為不同照片,整檔 sha256 正好符合這個定義。
- 判斷:`(size, mtime)` 沒變就跳過雜湊,重新掃描時只需要讀變動過的檔案。
- 判斷:用雜湊重新連結「找不到原檔」的照片,讓在系統外搬動檔案不會弄丟相簿歸屬。

**考慮過的替代方案**: 感知雜湊(pHash 等):會把不同解析度或編輯過的版本當成重複,違反 spec。用路徑當身分:搬動檔案就會變成一張新照片,原本的相簿歸屬會遺失。

## R9. 瀏覽器端的圖片顯示(SC-003)

**決策**: 縮圖是 256px WebP,匯入時產生,存在 `/data/thumbs/ab/cd/<sha256>.webp`。大圖預覽是 1600px WebP,**第一次請求時才產生**並快取。回應都加 `Cache-Control: public, max-age=31536000, immutable`(網址裡含雜湊)。

**理由**:

- 查證(caniuse.com「HEIF/HEIC image format」):Chrome 和 Firefox 無法顯示 HEIC 原檔,必須轉檔。
- 判斷:縮圖檔放在檔案系統而不是 DB BLOB,避免 MySQL 膨脹,也能直接 sendFile。
- 估算(R1 的完整解碼實測 1.2–1.5 秒):HEIC 第一次開預覽時要用 `heif-dec` 完整解碼,最壞情況約 1.3–1.5 秒。這段時間前端先把縮圖放大顯示,疊上載入指示(超過 1 秒要有指示)。之後再開就是快取檔,幾乎即時。
- 判斷:第一版**不**在匯入時預先產生預覽,因為那會讓匯入時間回到「每張都完整解碼」(R1)。

**考慮過的替代方案**: 縮圖存成 DB BLOB(MySQL 會膨脹,也不能直接 sendFile)、匯入時預先產生預覽(匯入時間回到每張完整解碼,見 R1)。

## R10. 只限內網存取(NFR-005、SC-007)

**決策**: 三層防護:

1. **不對外開 port**:路由器沒有把 NAS 的 8095 轉發出去。MySQL 完全不開 host port。
2. **NPM 存取清單**:在閘道機的 NPM 建立 proxy host `photos.home.example → 10.0.0.10:8095`,掛 Access List「只允許 `10.0.0.0/24` 與 VPN 網段,其他一律拒絕」。
3. **應用程式本身的 allowlist**:Fastify `trustProxy` 只信任 NPM 的 `10.0.0.2`。client IP 不在 `ALLOWED_CIDRS` 內就回 403。

**理由**:

- 查證(Cloudflare DNS 紀錄、路由器 port forwarding 設定):Cloudflare 有公開的萬用 A 紀錄,指向私有 IP `.179`,一般外部使用者連不到;但 NPM 的 443 本來就對外轉發(`cloud.example.com` 經過它)。
- 判斷:所以第 2 層不能省。外部只要直接連公網 IP、帶上 `Host: photos.home.example`,請求就會被 NPM 代理進來。
- 判斷:驗證必須從外部做,因為在 LAN 內 curl 公網 IP 會被 NAT hairpin 繞回內網,結果不可信。改用 check-host.net 或手機行動網路(V-SEC-1)。

**考慮過的替代方案**: 只靠第 1 層「不對外開 port」:如上所述,NPM 的 443 已經對外,外部可以靠 `Host` 標頭進來。只靠 NPM 存取清單:NPM 設定一旦被改錯就沒有任何防線,所以應用程式本身再擋一層。

## R11. 測試工具鏈(使用者指定)

**決策**:

| 層級 | 工具 | 備註 |
|---|---|---|
| 後端 unit | `node:test`(原生)+ `--experimental-test-coverage` 與門檻參數 | 0 個額外套件。domain 層是純函式,注入 `clock` |
| 後端 integration / contract | `node:test` + 真的 MySQL 8.4(CI service,或本機 `docker compose -f deploy/compose.test.yml`) | 每個測試檔使用自己的 database(`photo_test_<pid>_<n>`),可平行執行 |
| 前端 unit | `vitest` + `jsdom` | 與 Vite 同一套設定 |
| E2E + 無障礙 | `@playwright/test` + `@axe-core/playwright` | 每個 user story 至少一條主要路徑;`axe` 0 個違規 |
| 效能 | 自寫 seed 腳本灌 10,000 筆 + `autocannon`(dev 依賴)量 API p95;Playwright trace 量第一屏時間 | V-PERF 系列 |

- 測試圖片在測試中**現場產生**(用 sharp 產生帶 EXIF 的小 JPEG / PNG),不把大檔放進 repo。HEIC 樣本只準備一個小檔(< 50KB)放在 `fixtures/`。

**理由**:

- 判斷:使用者要求每一層都有測試。後端用原生 `node:test`,不必多加套件;前端用 vitest,和 Vite 共用設定。
- 判斷:integration 測試接真的 MySQL 8.4,因為 R4 的陷阱(collation、`dateStrings`、NULL 排序)只有在真的資料庫上才會出現。

**考慮過的替代方案**: 後端也用 vitest(多一個依賴,`node:test` 已經夠用)、integration 改用 SQLite 或 mock(抓不到 R4 那些 MySQL 專屬的行為)、把真實照片放進 repo 當 fixture(檔案太大;現場產生的小圖已經能涵蓋 EXIF 的情況)。

## R12. CI 與部署(FR-015、SC-006)

**決策**:

- **CI**:GitLab CI(`.gitlab-ci.yml`)。stage 依序是 lint、typecheck、unit、integration (帶 `mysql:8.4` service)、e2e、build。build 階段把 image 推到`registry.home.example/tools/photo-albums`。
- **Image 基底**:`node:22-trixie-slim`,另外用 apt 安裝 `heif-thumbnailer`、`libheif-examples`(提供 `heif-dec`)、`libheif-plugin-libde265` 和 `perl`(給 exiftool)。必須是 **trixie**:bookworm 的 libheif 1.15 沒有拆出 `heif-thumbnailer` 套件(實測時 apt 找不到這些套件)。
- **部署**:一個 compose stack,兩個 service(`app`、`mysql`),透過 Unraid Compose Manager 的 GUI 啟停。CLI 只用來查狀態,而且要加 `-p photo_albums`(踩雷紀錄:GUI 用底線命名)。
- **掛載**:
  - 照片 share 掛到 `/photos`,**`:ro` 唯讀**。這讓 FR-015 和 SC-006「原檔零改動」在核心層級就有保證,不靠程式自律。
  - appdata(`/srv/appdata/photo-albums/data`)掛到 `/data`(縮圖)。
- **Port**:`8095`。對照 NAS 現況,這個 port 沒有被占用。部署前會再查一次 `get_port_conflicts`。
- **機密**:MySQL 密碼存在 密碼庫,部署時寫進 stack 目錄的 `.env`(權限 0600)。repo 裡只有 `.env.example` 和 `$VAR` 佔位。

**理由**:

- 實測(`node:22-bookworm-slim` 容器內 `apt-get install heif-thumbnailer`):找不到套件;trixie 才有 libheif 1.23 拆出的 `heif-thumbnailer`。
- 實測(對照 NAS 現況的 port 使用清單):8095 沒有被占用,部署前再用 `get_port_conflicts` 查一次。
- 判斷:照片以 `:ro` 掛載,在核心層級保證原檔不會被改動。
- 判斷:Unraid 上的 Docker 服務必須走 GUI 啟停,所以部署方式選 Compose Manager。

**考慮過的替代方案**: `node:22-bookworm-slim`(libheif 1.15 沒有 `heif-thumbnailer`,實測 apt 找不到)、照片以讀寫掛載並靠程式不去寫(SC-006 就要靠程式自律,而不是由核心保證)。

## 待驗證

| 來源 | 待驗證 | 驗證方式 / 時機 | 擋計畫? |
|---|---|---|---|
| R1 | 真實 HEIC 的內嵌縮圖命中率(`thumb_source`) | V-PERF-1 | 否 |
| R2 | 1,000 張在 5 分鐘內匯入完成(目前只是估算) | V-PERF-1,在 NAS 用真實照片 | 否 |
| R10 | 從外網連不進來 | V-SEC-1,用 check-host.net 或手機行動網路 | 否 |
| R10 | OpenVPN 的 client 網段 | 部署時從 live 設定讀取,不從筆記抄 | 否 |
| R12 | port 8095 仍未被占用 | 部署前用 `get_port_conflicts` 再查一次 | 否 |

## 修訂紀錄

### 2026-10-16

- R1:HEIC 縮圖從「`heic-decode`(wasm)完整解碼」改成「`heif-thumbnailer` 優先讀內嵌縮圖」。原因:實測有內嵌縮圖時快約 47 倍(每張 26–27ms 對 1.55–1.69 秒)。連帶:R2 拿掉 `worker_threads` 池,HEIC 改在子行程解碼;R12 的 image 基底改用 trixie。
