# 道館:組合三支 Skills(git / TBD / 雙菱形)

這一頁是本座道館的證據索引:題目要的三樣東西各在哪裡,以及每一項功能對得上哪幾筆 commit。

## 三項完成條件

| 題目要的 | 位置 | 狀態 |
|---|---|---|
| 三支 Skill 的完整資料夾 | [`git-conventional-commit`](../../.claude/skills/git-conventional-commit/) · [`trunk-based-development`](../../.claude/skills/trunk-based-development/) · [`double-diamond-principle`](../../.claude/skills/double-diamond-principle/)(`.agents/skills/` 內容相同) | 已就位 |
| 同一個專案完成五到八個功能後的所有 git commits 紀錄 | [`git-log.txt`](./git-log.txt)(39 筆,含每一筆的完整訊息)· 線上:[BDGG_blog 的 commit 列表](https://github.com/YongRui0402/BDGG_blog/commits/main) | 已匯出 |
| 人類觀察:哪些原則有被遵循、哪些沒有、從哪個實際結果看出來、優化空間 | [`觀察紀錄.md`](./觀察紀錄.md) | 尚未填寫 |

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
* **當時的 Skill 版本**是本 repo 的 commit,連結會打開那個時間點的三支 skill。記這一欄是為了觀察時分得出來:某條原則沒被遵循,是那時的 Skill 還沒寫到,還是寫了但 Agent 沒照做。`a18acf7` 的提交時間(17:29)晚於功能 3 完成(17:13)—— 專案是透過連結直接讀本 repo 工作目錄裡的 skill,這一版做完前三項才提交。之後依後五項心得修訂的 [`1055ab8`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/1055ab8/.claude/skills) 是目前的版本,還沒有在專案上用過。

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

## commit 紀錄是怎麼匯出的

2026-10-05 在專案 repo 的 `8cc3b6d`(當時的 `main`)執行:

```bash
git log --all --graph --decorate --date=iso --format='%h %ad %d%n    %s%n%w(0,4,4)%b' > ~/Desktop/BDGG-Dev-Skills/docs/task1_skill_creator/git-log.txt
```

`--all --graph` 是為了連短期 branch 的分岔與合併都留下來,只看 trunk 的直線歷史判斷不出 branch 活了多久。最新的在最上面。
