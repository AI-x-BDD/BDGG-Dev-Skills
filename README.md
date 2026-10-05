# BDGG-Dev-Skills

## 關於這個 repo

我在這個 repo 整理開發流程相關的 skills,用來解決「每次都要重新跟 Agent 交代同一套做事方法」的問題:動手前怎麼釐清問題、變更怎麼切小並整合回主幹、commit 訊息怎麼寫。

做法來自水球軟體學院《AI x BDD》課程:先請 Agent 讀完一份關鍵文獻與它的延伸頁面,再用 `/skill-creator` 把內容整理成 skill,最後拿到真實的專案上連續使用,由人來觀察 Agent 有沒有照著做。

各座道館的 skills 都累積在這個 repo,每次繳交用 tag 標記當時的版本。

## 結構說明

| 路徑 | 內容 |
|---|---|
| `.claude/skills/` | Claude Code 格式的 skills(正本) |
| `.agents/skills/` | Codex／.agents 格式的 skills,內容與 `.claude/skills/` 一致 |
| `docs/task<N>_<主題>/` | 各座道館的證據:專案說明、commit 紀錄、人類觀察 |
| `VERSION` | template 版本 |

> `.claude/skills/`、`.agents/skills/`、`VERSION` 是《AI x BDD》課程平台抓取與展示 skills 的固定位置,請勿更名、搬移或刪除。

## 道館作業

| 道館 | 繳交版本 | 證據 |
|---|---|---|
| 組合三支 Skills(git / TBD / 雙菱形) | tag `task1-v1`(尚未建立) | [`docs/task1_skill_creator/`](./docs/task1_skill_creator/) |

### 組合三支 Skills(git / TBD / 雙菱形)

1. 請 Agent 分別研究三份官方文獻與站內延伸頁面,用 `/skill-creator` 寫成三支可以分別啟用的 skill。
2. 選一個小型軟體專案,拆成五到八個功能。每次只開發一個,開發前依序啟用 `/double-diamond-principle` → `/git-conventional-commit` → `/trunk-based-development`。
3. 匯出專案的所有 git commits,由我逐一對照:哪些原則有被遵循、哪些沒有、從哪個實際結果看出來、還有什麼優化空間。
4. 錄一段約一分鐘的影片介紹產出,連同這個 repo 的網址貼到課程平台的道館頁。

進度:三支 skill 尚未建立;專案、commit 紀錄與觀察紀錄尚未開始。

## Skills 與設計想法

### `git-conventional-commit`

- **用途**:讓 Agent 依 Conventional Commits 1.0.0 寫 commit 訊息,並把不相關的變更拆成不同的 commit。
- **使用時機**:每次要提交變更之前。
- **設計想法**:(skill 完成後補上)
- **資料來源**:<https://www.conventionalcommits.org/en/v1.0.0/>
- **驗證狀態**:尚未建立。

### `trunk-based-development`

- **用途**:讓 Agent 以主幹式開發的方式整合變更 —— 功能切小、使用 trunk 或短期 branch、整合前先跑測試、讓 trunk 隨時可以發布。
- **使用時機**:開始一個功能、要開 branch 或要整合回 trunk 的時候。
- **設計想法**:(skill 完成後補上)
- **資料來源**:<https://trunkbaseddevelopment.com/>
- **驗證狀態**:尚未建立。

### `double-diamond-principle`

- **用途**:讓 Agent 在動手寫程式之前,先走過雙鑽石的發散與收斂 —— 理解使用者與問題、收斂這次的範圍、提出可能的做法、選定後先小範圍測試。
- **使用時機**:收到一個新的功能需求、還沒開始實作的時候。
- **設計想法**:(skill 完成後補上)
- **資料來源**:<https://www.designcouncil.org.uk/resources/framework-for-innovation/>
- **驗證狀態**:尚未建立。

### `skill-creator`(工具,非我的作品)

- **用途**:建立、修改與評測 skill。上面三支 skill 都透過它產生。
- **來源**:取自 Anthropic 官方的 skill-creator,依 Apache-2.0 授權隨附 `LICENSE.txt`,內容未經我改寫。

## 交流

這些 skills 歡迎直接取用,或依你的專案調整。如果有使用上的問題或改進建議,歡迎開 issue 與我討論。

---

## 官方宣告（以下區塊請保留）

本 repo 為[水球軟體學院](https://world.waterballsa.tw)《AI x BDD：規格驅動全自動化開發術》課程的學員產出，用於公告課程中道館作業的展示，並依[官方 Template](https://github.com/AI-x-BDD/aixbdd-skill-homework-template) 建立。

《AI x BDD：規格驅動全自動化開發術》課程四大特色：

1. **【軟工方法論＋結果導向】**
   只談 AI coding 不談軟工方法論，是不學無術！課程中強調結果導向的開發方法：只要訂好驗收標準，就可以 One-Shot 開發到位！
2. **【最完整的 SDD 概念與實作】**
   市面上最完整的 SDD 課程，一次教你 Skills、SDD、TDD、BDD 的知識與實踐，輕鬆實踐高效可靠全自動開發。
3. **【企業級實戰導入】**
   用企業級實踐導入高規格，不只學會工具，更知道如何舉一反三完全客製化企業專案需求。
4. **【課程教學方式與物超所值】**
   這是一堂理論、實務跟實戰三者兼具的 SDD 線上課程，用工作坊級別的學習體驗，不是只是教概念，而是直接帶著做！

[了解更多課程內容說明](https://waterballs.tw/Ghl6O)

## 開源專案：AI x BDD

水球老師把這套 AI x BDD 的方法論做成開源 pipeline skill：把產品迭代寫成 Gherkin，再一路帶到 RED → GREEN → REFACTOR。

覺得有幫助，歡迎給它一顆 Star：

[![Star Waterball-Software-Academy/aixbdd](https://img.shields.io/github/stars/Waterball-Software-Academy/aixbdd?style=social)](https://github.com/Waterball-Software-Academy/aixbdd)

## 相關問題洽詢管道

1. [水球軟體學院 LINE 官方帳號](https://lin.ee/STIsOLZ)
2. 客服信箱：[support@waterballsa.tw](mailto:support@waterballsa.tw)
3. [水球軟體學院（社群）Discord](https://discord.gg/Ymjz7NmZXn)

---

© 2026 水球球特務有限公司版權所有，侵害必究。
