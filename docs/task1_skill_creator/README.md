# 道館:組合三支 Skills(git / TBD / 雙菱形)

這一頁是本座道館的證據索引:題目要的三樣東西各在哪裡,以及每一項功能對得上哪幾筆 commit。

## 三項完成條件

| 題目要的 | 位置 | 狀態 |
|---|---|---|
| 三支 Skill 的完整資料夾 | [`git-conventional-commit`](../../.claude/skills/git-conventional-commit/) · [`trunk-based-development`](../../.claude/skills/trunk-based-development/) · [`double-diamond-principle`](../../.claude/skills/double-diamond-principle/)(`.agents/skills/` 內容相同) | 已就位 |
| 同一個專案完成五到八個功能後的所有 git commits 紀錄 | [`git-log.txt`](./git-log.txt)(39 筆,含每一筆的完整訊息)· 線上:[BDGG_blog 的 commit 列表](https://github.com/YongRui0402/BDGG_blog/commits/main) | 已匯出 |
| 人類觀察:哪些原則有被遵循、哪些沒有、從哪個實際結果看出來、優化空間 | [`觀察紀錄.md`](./觀察紀錄.md) | 已填寫 |

繳交版本:tag `task1-v1`(尚未建立)。

## 專案

* 名稱:BDGG_blog
* 一句話說明:用 Hugo 產生、GitHub Actions 建置、GitHub Pages 託管的個人部落格 —— 寫 Markdown、`git push` 就上線
* repo:<https://github.com/YongRui0402/BDGG_blog>(公開)
* 站台:<https://yongrui0402.github.io/BDGG_blog/>

專案開成**獨立的公開 repo**,不放在這個 Skill repo 裡。這題的證據就是 commit 紀錄本身,而且要看 trunk 有沒有維持可發布 —— 跟 Skill 的修改混在同一條歷史裡,兩件事都看不清楚。

## 功能清單(8 項功能 + 收尾,一次只開發一個)

每次開發前依序啟用 `/double-diamond-principle` → `/git-conventional-commit` → `/trunk-based-development`,再貼上該項的需求。

| # | 功能 | 需求原文 | commits(依時間順序) | Agent 當下的心得 | 當時的 Skill 版本 |
|---|---|---|---|---|---|
| 1 | **push 就上線**<br>push 到 `main` 之後自動建置,最簡單的頁面出現在公開網址 | [features.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L778-L814) | 6 筆:`chore` [7beca00](https://github.com/YongRui0402/BDGG_blog/commit/7beca00) · `feat` [886fd2d](https://github.com/YongRui0402/BDGG_blog/commit/886fd2d) · `ci` [43672b8](https://github.com/YongRui0402/BDGG_blog/commit/43672b8) · `test` [1e09eca](https://github.com/YongRui0402/BDGG_blog/commit/1e09eca) · `revert` [fb80377](https://github.com/YongRui0402/BDGG_blog/commit/fb80377) · `docs` [e454680](https://github.com/YongRui0402/BDGG_blog/commit/e454680) | [skill-notes.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/skill-notes.md?plain=1#L163-L220) | [`a18acf7`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/a18acf7/.claude/skills) |
| 2 | **基本版面**<br>頁首選單、頁尾、深色模式、手機版面與基本的 404 頁 | [features.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L818-L851) | 4 筆:`feat` [d7fb342](https://github.com/YongRui0402/BDGG_blog/commit/d7fb342) · `feat` [de38387](https://github.com/YongRui0402/BDGG_blog/commit/de38387) · `feat` [5ce4506](https://github.com/YongRui0402/BDGG_blog/commit/5ce4506) · `docs` [c4017a1](https://github.com/YongRui0402/BDGG_blog/commit/c4017a1) | [skill-notes.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/skill-notes.md?plain=1#L222-L287) | [`a18acf7`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/a18acf7/.claude/skills) |
| 3 | **文章頁的閱讀體驗**<br>發第一篇文章;程式碼上色與一鍵複製、目錄、手機上好讀 | [features.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L855-L890) | 4 筆:`feat` [e1dbe9d](https://github.com/YongRui0402/BDGG_blog/commit/e1dbe9d) · `feat` [cc65de4](https://github.com/YongRui0402/BDGG_blog/commit/cc65de4) · `post` [5cf28ba](https://github.com/YongRui0402/BDGG_blog/commit/5cf28ba) · `docs` [f72ddec](https://github.com/YongRui0402/BDGG_blog/commit/f72ddec) | [skill-notes.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/skill-notes.md?plain=1#L289-L356) | [`a18acf7`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/a18acf7/.claude/skills) |
| 4 | **被找到與被訂閱**<br>canonical 與社群分享的 meta、RSS、sitemap | [features.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L894-L919) | 4 筆:`feat` [bbe543b](https://github.com/YongRui0402/BDGG_blog/commit/bbe543b) · `feat` [419ca0d](https://github.com/YongRui0402/BDGG_blog/commit/419ca0d) · `feat` [f02894e](https://github.com/YongRui0402/BDGG_blog/commit/f02894e) · `docs` [e4fd861](https://github.com/YongRui0402/BDGG_blog/commit/e4fd861) | [skill-notes.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/skill-notes.md?plain=1#L358-L435) | [`f2e8761`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/f2e8761/.claude/skills) |
| 5 | **分區與首頁列表**<br>六個分區的列表頁、首頁與「最新」頁、分頁與排序 | [features.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L923-L953) | 4 筆:`feat` [8f9830a](https://github.com/YongRui0402/BDGG_blog/commit/8f9830a) · `feat` [165c530](https://github.com/YongRui0402/BDGG_blog/commit/165c530) · `feat` [1bab068](https://github.com/YongRui0402/BDGG_blog/commit/1bab068) · `docs` [95b0760](https://github.com/YongRui0402/BDGG_blog/commit/95b0760) | [skill-notes.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/skill-notes.md?plain=1#L437-L515) | [`f2e8761`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/f2e8761/.claude/skills) |
| 6 | **標籤**<br>標籤頁與標籤總覽,文章上的標籤可以點 | [features.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L957-L980) | 3 筆:`feat` [84550ff](https://github.com/YongRui0402/BDGG_blog/commit/84550ff) · `feat` [4b71f0a](https://github.com/YongRui0402/BDGG_blog/commit/4b71f0a) · `docs` [095dd3d](https://github.com/YongRui0402/BDGG_blog/commit/095dd3d) | [skill-notes.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/skill-notes.md?plain=1#L517-L579) | [`f2e8761`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/f2e8761/.claude/skills) |
| 7 | **關於頁**<br>BDGG 是誰、做過什麼、怎麼聯絡 | [features.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L984-L1013) | 4 筆:`fix` [30146cd](https://github.com/YongRui0402/BDGG_blog/commit/30146cd) · `feat` [f8ffcf0](https://github.com/YongRui0402/BDGG_blog/commit/f8ffcf0) · `refactor` [98777b8](https://github.com/YongRui0402/BDGG_blog/commit/98777b8) · `docs` [60f4067](https://github.com/YongRui0402/BDGG_blog/commit/60f4067) | [skill-notes.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/skill-notes.md?plain=1#L581-L647) | [`f2e8761`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/f2e8761/.claude/skills) |
| 8 | **站內搜尋**<br>中英文關鍵字搜尋;404 頁也有搜尋框 | [features.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L1017-L1049) | 5 筆:`refactor` [5dbc145](https://github.com/YongRui0402/BDGG_blog/commit/5dbc145) · `feat` [e5641ee](https://github.com/YongRui0402/BDGG_blog/commit/e5641ee) · `feat` [5fd403a](https://github.com/YongRui0402/BDGG_blog/commit/5fd403a) · `docs` [d945f0d](https://github.com/YongRui0402/BDGG_blog/commit/d945f0d) · `docs` [4293b8c](https://github.com/YongRui0402/BDGG_blog/commit/4293b8c) | [skill-notes.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/skill-notes.md?plain=1#L649-L718) | [`f2e8761`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/f2e8761/.claude/skills) |
| — | **收尾(不算功能)**<br>逐項驗收、補完 README、彙整試用心得 | [features.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L1053-L1081) | 5 筆:`docs` [8c7afe9](https://github.com/YongRui0402/BDGG_blog/commit/8c7afe9) · `docs` [519489b](https://github.com/YongRui0402/BDGG_blog/commit/519489b) · `docs` [19f43be](https://github.com/YongRui0402/BDGG_blog/commit/19f43be) · `fix` [e3b8720](https://github.com/YongRui0402/BDGG_blog/commit/e3b8720) · `docs` [8cc3b6d](https://github.com/YongRui0402/BDGG_blog/commit/8cc3b6d) | [skill-notes.md](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/skill-notes.md?plain=1#L720-L765) | [`f2e8761`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/f2e8761/.claude/skills) |

* **需求原文**連到專案 repo 的 `docs/features.md`:每一項底下「貼上這段」就是下給 Agent 的那段話,後面接範圍與驗收條件。功能 3、7 的範本裡有 `<…>` 的欄位,是開發當下才填的,repo 裡留的是範本。
* **Agent 當下的心得**連到專案 repo 的 `docs/skill-notes.md`:每做完一項,由照著 skill 做事的 Agent 自己記的,不是人類的觀察。人類的觀察只在 [`觀察紀錄.md`](./觀察紀錄.md)。
* **當時的 Skill 版本**是本 repo 的 commit,連結會打開那個時間點的三支 skill。記這一欄是為了觀察時分得出來:某條原則沒被遵循,是那時的 Skill 還沒寫到,還是寫了但 Agent 沒照做。`a18acf7` 的提交時間(17:29)晚於功能 3 完成(17:13)—— 專案是透過連結直接讀本 repo 工作目錄裡的 skill,這一版做完前三項才提交;每一場實際載入的內容和表裡的 commit 相同,比對方法見下面的「查證紀錄」。之後依後五項心得修訂的 [`1055ab8`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/1055ab8/.claude/skills) 是目前的版本,還沒有在專案上用過。

## 依題目「你要觀察什麼」的四點找證據

| 題目要看的 | 可以核對的實際結果 |
|---|---|
| **Double Diamond**:先理解使用者與問題、收斂範圍、提出做法、小範圍測試、取得新資訊時回頭修正 | 專案 repo 的 [`docs/requirements.md`](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/requirements.md):[Discover](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/requirements.md?plain=1#L8) · [Define](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/requirements.md?plain=1#L134) · [Develop](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/requirements.md?plain=1#L231) · [Deliver](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/requirements.md?plain=1#L340) · [回頭修正](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/requirements.md?plain=1#L419)。每一項功能實測後定下的做法在 [`docs/features.md` 的「已定下的做法」](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/features.md?plain=1#L91) |
| **Trunk Based**:功能夠小、trunk 或短期 branch、整合前先跑測試、trunk 維持可發布、較長的變更用 feature flag 或 branch by abstraction | [`git-log.txt`](./git-log.txt) 的圖是一條直線:39 筆全部直接進 `main`,沒有 merge commit,remote 上只有 `main` 一個 branch。[GitHub Actions 的執行紀錄](https://github.com/YongRui0402/BDGG_blog/actions):32 次,31 次成功、1 次失敗 —— 失敗的是功能 1 刻意推的 [`1e09eca`](https://github.com/YongRui0402/BDGG_blog/commit/1e09eca)(驗證建置失敗時不會部署),下一筆 [`fb80377`](https://github.com/YongRui0402/BDGG_blog/commit/fb80377) 還原。逐筆取出重建的結果在 [`requirements.md` 驗收第 13 項](https://github.com/YongRui0402/BDGG_blog/blob/8cc3b6d/docs/requirements.md?plain=1#L406)。**短期 branch、feature flag、branch by abstraction 在這個專案一次都沒有用到**(單人、每項功能當天做完) |
| **Conventional Commits**:不相關的變更拆開、格式與 type 正確、破壞相容性的變更明確標示 | [`git-log.txt`](./git-log.txt)。type 分布:`feat` 17、`docs` 13、`refactor` 2、`fix` 2,`chore`、`ci`、`test`、`revert`、`post` 各 1。用 skill 隨附的檢查腳本對整段歷史跑:39 筆,0 筆不符規範,1 個提醒(`post` 是自訂的 type)。**沒有出現 scope 與 breaking change**,這兩條規則在這個專案沒有被考驗到 |
| **完成後的回報**:這次怎麼用 Double Diamond、測試結果、branch 與整合狀態、實際的 commit message | 回報本身是對話裡的輸出,沒有逐字存進 repo。repo 裡對得上的是每一項結尾的那筆 `docs:` commit(上表各列的最後一筆,訊息本文列出這一項更新了哪些紀錄),以及上表「Agent 當下的心得」 |

檢查腳本可以自己重跑(只用 Python 標準函式庫):

```bash
git clone https://github.com/YongRui0402/BDGG_blog && git clone https://github.com/AI-x-BDD/BDGG-Dev-Skills
python3 BDGG-Dev-Skills/.claude/skills/git-conventional-commit/scripts/check_commit_msg.py -C BDGG_blog --range HEAD
```

## 查證紀錄

寫觀察紀錄時,有幾項從 repo 看不出來,所以請 Agent 另外查了三個來源。這一節只放查到的事實;判斷在 [`觀察紀錄.md`](./觀察紀錄.md)。查證日期 2026-10-05,時間都是 +08:00。

| 來源 | 內容 | 審查者能不能重查 |
|---|---|---|
| 對話紀錄 | Claude Code 存在本機的 session log:開發前討論需求一場、8 項功能各一場(功能 4 接在修訂 skill 的那一場後面)、收尾一場 | 不能,沒有公開。下面是從裡面取出的計數與摘錄 |
| git 歷史與 GitHub Actions | 專案 repo 的 39 筆 commit、32 次執行紀錄 | 可以 |
| 逐筆重建 | 把每一筆 commit 用 `git archive` 取到暫存目錄,連上同一份 Hugo(0.165.0),跑 `make check` | 可以,指令在本節最後 |

### 每一項功能的實際數字

| # | 載入的 Skill 版本 | 對話(開工 → 最終回報) | 開工後問使用者的題數 | 變更量(不含 `docs/`) | 逐筆重建 | 沒有自己 CI 紀錄的 commit |
|---|---|---|---|---|---|---|
| 1 | `a18acf7` | 16:05 → 16:28 | 3 | 15 檔 +500 | 6 筆:4 通過、1 失敗(`1e09eca`,刻意的)、1 無法建(`7beca00`,當時還沒有 Makefile) | `7beca00`、`886fd2d` |
| 2 | `a18acf7` | 16:29 → 16:49 | 4 | 14 檔 +855 −34 | 4 筆全過 | `d7fb342`、`de38387` |
| 3 | `a18acf7` | 16:55 → 17:14 | 1 | 14 檔 +529 −10 | 4 筆全過 | `e1dbe9d` |
| 4 | `f2e8761` | 17:50 → 18:04 | 0 | 10 檔 +403 −14 | 4 筆全過 | — |
| 5 | `f2e8761` | 18:25 → 18:44 | 0 | 23 檔 +365 −31 | 4 筆全過 | — |
| 6 | `f2e8761` | 18:48 → 19:03 | 0 | 11 檔 +94 −15 | 3 筆全過 | — |
| 7 | `f2e8761` | 19:04 → 19:18 | 3 | 6 檔 +42 −16 | 4 筆全過 | — |
| 8 | `f2e8761` | 19:21 → 19:43 | 0 | 12 檔 +535 −15 | 5 筆全過 | `5dbc145` |
| 收尾 | `f2e8761` | 19:46 → 20:16 | 0 | 2 檔 +63 −8 | 5 筆全過 | `519489b` |

* **Skill 版本**是比對內容得來的:每一場對話啟用 skill 時,載入的全文會留在對話紀錄裡;拿它和本 repo 各個 commit 的 `SKILL.md` 比雜湊。三支 skill、每一場都對得上表裡那一個 commit,沒有對不上的。
* **逐筆重建**合計 39 筆:37 筆通過、1 筆失敗、1 筆無法建。失敗的那一筆是功能 1 刻意推的,它同時是檢查器的對照組 —— 該擋的有擋。
* **沒有自己 CI 紀錄**的 7 筆都是和後面的 commit 一起 push,CI 只跑了最後一筆;逐筆重建裡這 7 筆除了還沒有 Makefile 的 `7beca00` 都通過。Actions 的 32 次執行是 31 次成功、1 次失敗(`1e09eca`)。

### Double Diamond:理解問題與收斂範圍發生在哪裡

* **開發前有一場專門討論需求的對話**(15:01 → 15:58,skill 版本 `a18acf7`)。Agent 分三輪問了 12 題:這個站和既有部落格的關係、最重要的是哪一點、寫給誰看、發文流程、要練的是什麼、身分與隱私、第一版的功能、技術偏好、起點用哪一版原始碼、網址、舊內容帶不帶、公開到什麼程度。使用者中途更正過方向(不匿名、照既有架構、原始碼在 GitLab、只要 8 項),每一次都記在 `requirements.md` 的「回頭修正」。產出就是專案 repo 的 `requirements.md` 與 `features.md`。
* **各項功能開工後問的題目**(題數見上表):
  * 功能 1:同意第一次 push 到公開 repo、「建置失敗時不會部署」要怎麼驗、一個空檔要怎麼處理
  * 功能 2:標語用哪一組、分享圖怎麼處理、預覽標記留不留、看外觀截圖
  * 功能 3:起草好的第一篇文章要不要發布
  * 功能 7:工作經歷寫什麼、技能用哪一份、頁面其餘文字可不可以
  * 功能 4、5、6、8:沒有問
* **兩版 skill 在這件事上寫的是同一個方向**:需求已經很明確(附了驗收條件或完整規格)時,Discover 縮成查核「規格有沒有和現況矛盾」。[`a18acf7` 第 119 行](https://github.com/AI-x-BDD/BDGG-Dev-Skills/blob/a18acf7/.claude/skills/double-diamond-principle/SKILL.md?plain=1#L119)、[`f2e8761` 第 122 行](https://github.com/AI-x-BDD/BDGG-Dev-Skills/blob/f2e8761/.claude/skills/double-diamond-principle/SKILL.md?plain=1#L122)。這個專案的 8 項功能都落在這一列;「需求模糊時會不會先問」只在開發前那一場出現過。
* **Agent 沒問就自己決定、做完才報的三次**:功能 5(空的分區自動不掛選單)、功能 6(同一個標籤兩種寫法並存時讓建置失敗)、功能 8(沒有照規格用 `data-baseurl`;關於頁不進搜尋)。三次都放在最終回報的最前面,功能 8 的原文是「沒有照規格用 `data-baseurl`,而且沒先問你」。當時的 skill 把要問的事分成兩種,其中「可以帶著做出來的東西去問」的期限是「任何公開或難以還原的動作之前(發布、push 到會自動部署的 branch…)」([`f2e8761` 第 79–80 行](https://github.com/AI-x-BDD/BDGG-Dev-Skills/blob/f2e8761/.claude/skills/double-diamond-principle/SKILL.md?plain=1#L79-L80));這三個決定都是 push 上線之後使用者才看到。Design Council 的原文沒有規定這件事,這是 skill 的詮釋。

### Trunk Based

* **功能夠不夠小**:skill 的標準是「動手後幾個小時內,上限一兩天」([`f2e8761` 第 43 行](https://github.com/AI-x-BDD/BDGG-Dev-Skills/blob/f2e8761/.claude/skills/trunk-based-development/SKILL.md?plain=1#L43))。每一場對話從開工到最終回報是 14 到 23 分鐘。Agent 自己說偏大的只有一次:功能 5 的第一筆 `8f9830a`(18 個檔案),回報寫「canonical 的修正其實可以先單獨送,這次沒有拆」。
* **刻意弄壞 trunk 的那一筆**是使用者的決定:功能 1 的對話裡(16:16)Agent 問「『建置失敗時公開站仍是上一版』這一項要怎麼驗」,使用者選「照原文推到 main 再 revert」。紅燈從 `1e09eca`(16:24)到 `fb80377`(16:26)。
* **一次推好幾筆**:前三項用的 `a18acf7` 沒有提這件事;`f2e8761` 補了一句「一次推出好幾筆 commit 時,CI 通常只跑最後一筆;中間那幾筆只有本機驗過,所以每一筆都要在本機各自建置過」([第 88 行](https://github.com/AI-x-BDD/BDGG-Dev-Skills/blob/f2e8761/.claude/skills/trunk-based-development/SKILL.md?plain=1#L88))。Agent 在功能 2、3、8 的回報裡主動講了哪幾筆只有本機驗過。
* **一次檢查命中卻照推**:功能 4 的回報寫「最後一筆 push 前,我自己加的內網字樣檢查命中 2 行,指令卻沒有停下來就推了」;事後查是文件裡描述檢查項目的字樣,不是真的位址。
* **feature flag / branch by abstraction**:沒有用到,也沒有出現做不完的長變更。沾得上邊的只有 `hugo.toml` 的 `disableKinds`:功能 1(`886fd2d`)先關掉 6 種還沒做的頁面,之後每做到一種就打開(`de38387`、`419ca0d`、`f02894e`、`8f9830a`),功能 6(`84550ff`)整行拿掉;中途功能 3(`e1dbe9d`)多關了一種,功能 5 打開。

### Conventional Commits

* **破壞相容性的變更**:`!` 與 `BREAKING CHANGE` 在 39 筆裡是 0;8 場的最終回報都寫「沒有 breaking change」。第一篇文章發布之後,文章的網址規則沒有再改過。唯一讓已經上線的網址消失的是 `d7fb342`:刪掉功能 1 的測試頁 `/link-test/`(上線約 20 分鐘),訊息本文有寫「功能 1 的連結測試頁與它的選單項目拿掉」,沒有標成破壞性變更。
* **自訂的 `post` type**(`5cf28ba`):規範第 14 條允許 `feat`、`fix` 以外的 type;commitlint 的預設設定(`@commitlint/config-conventional`)不收,skill 的檢查腳本給一個提醒。Agent 在功能 3 的回報裡主動講了這件事:「不喜歡的話從下一篇換掉」。
* **scope**:39 筆都沒有用。

### 完成後的回報

8 場對話的最後一則訊息,對照題目要的四件事:

| 題目要的 | 涵蓋 |
|---|---|
| 測試結果 | 8 場都有,以驗收條件逐列的表格呈現 |
| branch 與整合狀態 | 8 場都有,寫明直接進 `main`、沒有開 branch,以及 CI 的結果 |
| 實際的 commit message | 6 場列出原文(功能 6 的第三筆有節略);功能 1、8 列的是 hash、type 與改寫過的說明 |
| 這次怎麼用 Double Diamond | 3 場有專門一段(功能 3、6、7);功能 1、2、4、5、8 的內容散在「規格沒料到的事」「和規格不一樣的地方」這類段落,沒有以 Double Diamond 的階段交代 |

專案 repo 的 `skill-notes.md` 提到 Agent「被提醒要回報進度」的次數(功能 6、7、8 與收尾是 6、2、6、1)。對話紀錄裡,這幾場的系統靜默提醒次數正好是 6、2、6、1 —— 提醒來自工具,不是使用者中途打字。

### 自己重跑

```bash
git clone https://github.com/YongRui0402/BDGG_blog && cd BDGG_blog
make check                      # 先在最新的那一筆跑一次,讓它下載 Hugo 到 .hugo-bin/
for h in $(git log --reverse --format=%h); do
  d=$(mktemp -d); git archive "$h" | tar -x -C "$d"
  [ -f "$d/Makefile" ] || { echo "SKIP $h"; continue; }
  ln -s "$PWD/.hugo-bin" "$d/.hugo-bin"
  (cd "$d" && make check >/dev/null 2>&1) && echo "ok   $h" || echo "FAIL $h"
done
```

## commit 紀錄是怎麼匯出的

2026-10-05 在專案 repo 的 `8cc3b6d`(當時的 `main`)執行:

```bash
git log --all --graph --decorate --date=iso --format='%h %ad %d%n    %s%n%w(0,4,4)%b' > ~/Desktop/BDGG-Dev-Skills/docs/task1_skill_creator/git-log.txt
```

`--all --graph` 是為了連短期 branch 的分岔與合併都留下來,只看 trunk 的直線歷史判斷不出 branch 活了多久。最新的在最上面。
