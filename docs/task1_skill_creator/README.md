# 道館:組合三支 Skills(git / TBD / 雙菱形)

這個目錄是本座道館的證據:三支 Skill 實際用在同一個小型專案上之後留下的紀錄。

| 項目 | 位置 |
|---|---|
| 三支 Skill | [`.claude/skills/`](../../.claude/skills/)(`.agents/skills/` 內容相同) |
| 繳交版本 | tag `task1-v1`(尚未建立) |
| 專案 repo | <待定> |
| 專案的 commit 紀錄 | [`git-log.txt`](./git-log.txt)(尚未匯出) |
| 人類觀察 | [`觀察紀錄.md`](./觀察紀錄.md) |

## 小型軟體專案

## 專案

* 名稱:<待定>
* 一句話說明:<待定>
* repo 位置:<待定>

專案開成**獨立的公開 repo**,不放在這個 Skill repo 裡。這題的證據就是 commit 紀錄本身,而且要看 trunk 有沒有維持可發布 —— 跟 Skill 的修改混在同一條歷史裡,兩件事都看不清楚。

## 功能清單(5~8 個,一次只開發一個)

| # | 功能 | 下給 Agent 的需求原文 | 當時的 Skill 版本(本 repo 的 commit) | 狀態 |
|---|---|---|---|---|
| 1 | | 請幫我開發 | | ☐ |
| 2 | | 請幫我開發 | | ☐ |
| 3 | | 請幫我開發 | | ☐ |
| 4 | | 請幫我開發 | | ☐ |
| 5 | | 請幫我開發 | | ☐ |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |

「當時的 Skill 版本」是為了觀察時分得出來:某條原則沒被遵循,是那時的 Skill 還沒寫到,還是寫了但 Agent 沒照做。

## 匯出 commit 紀錄

全部功能完成後,在專案 repo 裡執行:

```bash
git log --all --graph --decorate --date=iso --format='%h %ad %d%n    %s%n%w(0,4,4)%b' > ~/Desktop/BDGG-Dev-Skills/docs/task1_skill_creator/git-log.txt
```

`--all --graph` 是為了連短期 branch 的分岔與合併都留下來,只看 trunk 的直線歷史判斷不出 branch 活了多久。
