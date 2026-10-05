# <repo 名稱>

> 用這份 README 當範例，改成你自己的版本。repo 名稱請當成自己的作品集來命名。各節都可以改寫或刪除，只有文末的官方區塊要保留。

## 關於這個 repo

我在這個 repo 整理了 <主題> 相關的 skills，用來解決 <開發過程中遇到的問題>。

<!-- 範例：我在這個 repo 整理了從撰寫規格到 TDD 實作的 skills，做法來自水球軟體學院《AI x BDD》課程，讓 AI 產出的程式碼能逐條對應回規格。 -->

## 結構說明

| 路徑 | 內容 |
|---|---|
| `.claude/skills/` | Claude Code 格式的 skills |
| `.agents/skills/` | Codex／.agents 格式的 skills |
| `VERSION` | template 版本 |

> 以上路徑是《AI x BDD》課程平台抓取與展示 skills 的固定位置，請勿更名、搬移或刪除。

## 道館作業

<!-- 若本 repo 不是道館作業，可刪除本節。 -->

本 repo 用於繳交 <道館名稱>：

1. 我依《AI x BDD》課程平台道館頁列出的題目與完成條件，完成該館要求的 skills。
2. 我錄製了一支 3 分鐘內的 demo 影片，呈現 skill 的實際執行過程。
3. 我在《AI x BDD》課程平台的道館頁貼上本 repo 連結與影片連結，完成繳交。

## Skills 與設計想法

以下說明這個 repo 收錄的 skills，以及我設計時的考量。

<!-- 以下為範例，請替換成你自己的 skill；每個 skill 一則，維持用途／使用時機／設計想法／驗證狀態四項。 -->

### `gherkin-rule-check`

- **用途**：檢查 `.feature` 檔中每個 Scenario 是否只驗證一條規則，列出需要拆分的 Scenario。
- **使用時機**：寫完規格、交給 AI 產生測試程式碼之前。
- **設計想法**：一個 Scenario 混入多條規則時，AI 產生的測試容易漏掉其中一條。我先把規則拆開，後續的測試與實作就能逐條對應回規格。
- **驗證狀態**：已在個人專案中實際使用。

## 交流

這些 skills 歡迎直接取用，或依你的專案調整。如果有使用上的問題或改進建議，歡迎開 issue 與我討論。

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
