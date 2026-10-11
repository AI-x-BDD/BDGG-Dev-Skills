# 道館:自己做出 Skill Engineering,再用它優化道館一的三支 Skills

這一頁是本座道館的證據索引:題目要的東西各在哪裡、八支 Skill 怎麼分工、`/skill-engineering` 實際創建與優化了什麼。

## 完成條件

| 題目要的 | 位置 |
|---|---|
| 所有 Skills 的 skill package | [`.claude/skills/`](../../.claude/skills/)(17 支;`.agents/skills/` 內容相同) |
| 自己做出的 `/skill-engineering` | [`skill-engineering`](../../.claude/skills/skill-engineering/),以及它調度的七支 primitive |
| `/skill-engineering` 完成一次「創建 Skill」與一次「優化 Skill」的 git commit 紀錄 | 創建:[`f5dd87b`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/f5dd87b)(`skill-diagnose`)· 優化:[`04dda91`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/04dda91)(`trunk-based-development`;這一場從根因報告到驗收,form 與 derive 都有照順序叫用)。全部的紀錄見[創建與優化的紀錄](#skill-engineering-創建與優化的紀錄) |
| 道館一三支 Skills 的優化前版本與優化後版本 | 優化前:tag [`task1-v1`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/task1-v1/.claude/skills) · 優化後:tag [`task2-v1`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/task2-v1/.claude/skills)。對照見[三支 Skill 的優化前後](#三支-skill-的優化前後) |
| 人類觀察 | [`觀察紀錄.md`](./觀察紀錄.md) |

這座道館的全部變更:[`task1-v1...task2-v1`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/compare/task1-v1...task2-v1)。

## 第一題:八支 Skill 各自負責什麼

| Skill | 什麼時候用 | 負責什麼 | 不負責的交給誰 |
|---|---|---|---|
| [`skill-form-sop`](../../.claude/skills/skill-form-sop/) | 寫或改 `SKILL.md` 的 SOP | SOP 的格式:Phase 怎麼分、一行一步、每一步以動詞表的六個動詞之一開頭、分支只寫在行尾、資源只在用到的那一步點名。格式檢查與檔尾的流程圖由 `render_sop_diagram.py` 做 | 流程該有哪些步驟,由 `skill-engineering` 的藍圖決定 |
| [`skill-form-rule`](../../.claude/skills/skill-form-rule/) | 寫或改 `rules/` 底下的 Rule File | Rule 的格式:一條只管一件事、標 must 或 should、寫出為什麼、good 與 bad example 用同一個案例。結構由 `check_rule_file.py` 檢查 | 哪一步需要規則,由 `skill-derive-rule` 決定 |
| [`skill-derive-rule`](../../.claude/skills/skill-derive-rule/) | 已有 SOP,要替其中一步展開規則 | 決定展開哪一步、加哪幾條 Rule、落在哪個 Rule File、那一步改成什麼寫法,提案確認後才動 | Rule 交給 `skill-form-rule` 寫,那一步交給 `skill-form-sop` 改 |
| [`skill-form-template`](../../.claude/skills/skill-form-template/) | 寫或改 `templates/` 底下的樣板 | 樣板的格式:骨架與範例兩個檔成對、會變動的地方用 `{{名稱}}` 標出、範例是骨架填完的樣子。結構由 `check_templates.py` 檢查 | 哪一步需要樣板,由 `skill-derive-template` 決定 |
| [`skill-derive-template`](../../.claude/skills/skill-derive-template/) | 已有 SOP,要把其中一步的輸出格式固定下來 | 決定抽哪一步、樣板叫什麼、骨架有哪些填位符號、那一步改成什麼寫法,提案確認後才動 | 樣板交給 `skill-form-template` 寫,那一步交給 `skill-form-sop` 改 |
| [`skill-form-script`](../../.claude/skills/skill-form-script/) | 寫或改 `scripts/` 底下的腳本 | 腳本的格式:單檔 Python、第三方套件宣告在檔頭、輸入只走命令列參數、`--help` 說明用途與參數、結果寫 stdout、失敗時以非零結束。結構由 `check_scripts.py` 檢查 | 哪一步適合交給腳本,由 `skill-derive-script` 決定 |
| [`skill-derive-script`](../../.claude/skills/skill-derive-script/) | 已有 SOP,要把其中一步的機械工作交給程式 | 決定委派哪一步、腳本吃什麼吐什麼、那一步改成什麼寫法,提案確認後才動 | 腳本交給 `skill-form-script` 寫,那一步交給 `skill-form-sop` 改 |
| [`skill-engineering`](../../.claude/skills/skill-engineering/) | 創建一支新的 Skill,或對既有 Skill 跑出來的結果不滿意 | 找根因、定藍圖、驗收;見下表 | 任何一個部位都不自己寫,全部轉交上面七支 |

相鄰的兩支怎麼分開:

- **form 與 derive**:form 只回答「這個部位怎麼寫才合格」,derive 只回答「哪一步該長出這個部位、長出來之後那一步怎麼改寫」。derive 自己不寫檔。
- **四支 form 之間**:一支只管一種檔,各有自己的檢查腳本。
- **入口只有一個**:因為「產出不符預期」而來的修改請求,七支 primitive 的 `description` 都寫明先交給 `skill-engineering` 找根因([`a0cac58`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/a0cac58)、[`a9cb413`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/a9cb413))。

### `/skill-engineering` 怎麼組合它們

| Phase | 做什麼 | 轉交給誰 |
|---|---|---|
| 1 提出根因報告 | 優化時才做:用當時的輸入逐步演練 SOP,找出第一個偏離點,使用者同意才往下。創建新的 Skill 時跳過 | — |
| 2 提出藍圖 | 決定目標 Skill 的產出鏈、主幹與每一個部位,使用者同意才寫入。每一件要管的事依判定表由上往下選部位:結果只由輸入決定的放腳本,內容長什麼樣子的放樣板,需要判斷而且有人講明要把關的放規則,都不符合就不掛 | — |
| 3 寫出主幹 | 把藍圖的主幹寫成 `# SOP` | `skill-form-sop` |
| 4 寫出部位 | 既有的檔改寫成藍圖的樣子;新掛的部位一次掛一步 | 改寫:三支 `skill-form-*` · 新掛:三支 `skill-derive-*` |
| 5 列出驗收紀錄 | 把目標 Skill 複製到 `tmp/verify/`,交給不帶這場對話脈絡的 subagent 實跑,比對結果;有對不上的就回到藍圖 | subagent |

### 和題目不一樣的地方

- 題目寫規則強度用 Must / Should / May 三級;這裡的 Rule File 只有 must 與 should 兩級([`RuleFile-格式規範.md`](../../.claude/skills/skill-form-rule/rules/RuleFile-格式規範.md) 的〈每條 Rule 照固定格式寫〉)。
- 題目要八支;過程中另外長出 `skill-conform`(規範改了之後讓既有的 Skill 重新符合)與 `skill-diagnose`(根因不確定時的排查),兩支都是用 `/skill-engineering` 創建的。

## `/skill-engineering` 創建與優化的紀錄

時間是 +08:00。前半段在另一台機器上做,那裡的 commit 時間戳是 UTC,下表已換算。

| | 目標 Skill | 我當時下的指示(原話) | commit | 執行的 agent |
|---|---|---|---|---|
| 優化 | `git-conventional-commit` | 10-09 16:13「用/skill-engineering 來重建與優化 .claude/skills/git-conventional-commit」 | [`cee56be`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/cee56be)(16:51) | Claude Code |
| 優化 | `double-diamond-principle` | 10-10 00:12「/skill-engineering 優化.claude/skills/double-diamond-principle」,00:19 補充「我想將從目前的觀念指南重構成標準 SOP 流程（Phase / 步驟 / Rule）」 | [`aa5c56f`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/aa5c56f)(00:49) | Antigravity CLI |
| 優化 | `trunk-based-development` | 10-10 00:13「/skill-engineering 優化.claude/skills/trunk-based-development」 | [`57b8830`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/57b8830)(00:49) | Antigravity CLI |
| 創建 | `skill-diagnose` | 10-10 00:45「你可以先幫用 /skill-engineering 我抽成skill」 | [`f5dd87b`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/f5dd87b)(01:02) | Antigravity CLI |
| 創建 | `skill-conform` | 10-10 11:39 進入 `/skill-engineering`;12:35 提出「藍圖:skill-conform(新 skill,名字可改)」,12:48 與 13:18 各交一次驗收紀錄 | [`7d8dad2`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/7d8dad2)(13:18) | Claude Code |

之後又用 `/skill-engineering` 迭代了六場:

| 起因(我當時說的) | 動到的 Skill | commits |
|---|---|---|
| 10-10 19:42「/skill-engineering 迭代skill-form-sop」:流程圖與時序圖太長要移到檔尾、圖上的句子被截斷 | `skill-form-sop` 與全部 Skill 的 SOP | `4a018c0` `948dd9b` `ac2dfb7` `b5a36a9` `78728d5` `b8f454f` `d96f715` `e8861f3` |
| 10-11 00:10「我覺得舊的句子本來就應該重新改寫,我覺得應改把標記改成must?」 | `skill-form-sop`、`skill-conform` 與 16 支的 SOP | `dfdea5b` `f0d8823` `a4e4e5c` `6e7bc53` `fcac1ba` |
| 10-11 01:04「三步對不上要查一下,看起來不合理,是否為SOP動詞太少無法表達意圖」 | `skill-form-sop`、`trunk-based-development`、`double-diamond-principle` 與 7 支的回報步驟 | `65bdbfb` `fba5d5c` `0ea4e4a` `ed4bcff` `79688af` |
| 10-11 01:32 接手上一場實跑時記下的問題 | `skill-form-sop`、`double-diamond-principle`、`trunk-based-development` | `2daeb81` `1631152` `77a1bfd` `2281192` `4c7b49a` `655ceda` |
| 10-11 11:23「為何我覺得問題越修越多？」、11:27「我要開一個新的對話來改 skill-engineering,不然未來只會越改越多,疊床架屋」 | `skill-engineering` | `74c1843` `d5df95a` `cb03b43` |
| 10-11 18:01「好,先做第 1 項,用 /skill-engineering 修」、18:26「先改trunk-based-development 用 /skill-engineering」 | `double-diamond-principle`、`trunk-based-development` | `4a42fce` `0586f48` `04dda91` |

最後一場的經過:

- **叫用順序**:`double-diamond-principle` 是 `skill-engineering` → `skill-form-template`;`trunk-based-development` 是 `skill-engineering` → `skill-form-template` → `skill-form-rule` → `skill-derive-rule` → `skill-form-rule` → `skill-form-sop`。
- **驗收**:兩支各實跑一次(不帶脈絡的 subagent 在範例專案把功能做完),交出的紀錄都有新加的那一列。`trunk-based-development` 的規則另外做了對照審查:新版與重構當時的舊版不標示新舊,交給不帶脈絡的 subagent 逐條對照 `RuleFile-格式規範.md`。舊版 7 條裡有 6 條被判一條管好幾件事;新版第一次審有 2 條,改完重審是 0 條。
- **沒有做到的**:重審另外判了 2 條不過(一條的「為什麼」只是把要求倒過來講、一條沒有邊界案例),改掉之後沒有再送第三次審查;短期 branch 那條路需要 PR 與 review,沒有實跑過。實跑與審查的紀錄在 `tmp/verify/`,沒有進版控。

## 三支 Skill 的優化前後

| Skill | 優化前([`task1-v1`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/task1-v1/.claude/skills)) | 優化後 | 動到它的 commit |
|---|---|---|---|
| `git-conventional-commit` | [4 個檔](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/task1-v1/.claude/skills/git-conventional-commit):243 行的 `SKILL.md`、`references/`、`evals/`、1 支腳本 | [12 個檔](../../.claude/skills/git-conventional-commit/):2 個 Phase 共 8 步的 SOP、5 份 Rule File、2 組樣板、2 支腳本 | `cee56be` 重建 · `e8861f3` |
| `trunk-based-development` | [3 個檔](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/task1-v1/.claude/skills/trunk-based-development):249 行的 `SKILL.md`、`references/`、`evals/` | [6 個檔](../../.claude/skills/trunk-based-development/):4 個 Phase 共 13 步的 SOP、3 份 Rule File(共 22 條)、1 組樣板 | `57b8830` 重構 · `1201d81` `5a20536` `fba5d5c` `655ceda` `0586f48` `04dda91` |
| `double-diamond-principle` | [3 個檔](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/task1-v1/.claude/skills/double-diamond-principle):197 行的 `SKILL.md`、`references/`、`evals/` | [7 個檔](../../.claude/skills/double-diamond-principle/):4 個 Phase 共 12 步的 SOP、4 份 Rule File、1 組樣板 | `aa5c56f` 重構 · `1201d81` `0ea4e4a` `77a1bfd` `4c7b49a` `4a42fce` |

三支共通的還有格式遷移(`2927a67` `4a018c0` `ac2dfb7` `dfdea5b` `79688af`),以及拿掉沒有任何步驟會載入的 `references/` 與 `evals/`(`cee56be`、`2281192`)。

**資料來源改列在根目錄的 README**:道館一要求每條規則都能回到原始頁面核對。重構成 SOP 的時候,`SKILL.md` 文末的「資料來源」段沒有帶進新版;10-11 又把沒有任何步驟點名的 `references/` 清掉(`2281192`)。以含網址的行數算,Skill 資料夾裡 `trunk-based-development` 從 35 行變成 0 行,`double-diamond-principle` 從 14 行變成 0 行,`git-conventional-commit` 從 12 行變成 4 行(其中 1 行是規範本身,3 行是 uv 的安裝說明)。三支的出處與授權現在列在[根目錄 README 的「開發流程」](../../README.md#開發流程)底下,沒有放回 `SKILL.md`,因為它每次觸發都會整份載入;逐頁標出處的版本留在 `task1-v1`。

## 查證紀錄

查證日期 2026-10-11,當時的 `main` 是 `04dda91`;之後只動 `docs/` 與根目錄 README 的提交不算在內。這一節只放查到的事實;判斷在 [`觀察紀錄.md`](./觀察紀錄.md)。

| 來源 | 內容 | 審查者能不能重查 |
|---|---|---|
| git 歷史 | `task1-v1` 到 `04dda91` 的 87 筆 commit | 可以 |
| 對話紀錄 | Claude Code 的 session log 與 Antigravity CLI 的 transcript,分別存在做事的那兩台機器上 | 不能,沒有公開 |
| 檢查腳本 | `skill-conform` 的 `check_skills.py` | 可以,指令在本節最後 |

- **哪一筆 commit 是哪一場對話做的**:從對話紀錄只取三樣東西 —— 我打的訊息、Skill 的叫用、提交的時間 —— 再對上 git 歷史。上面兩張表的「原話」是照抄,錯字沒有改。
- **87 筆的 type 分布**:`feat` 40(其中 4 筆標 `!`)、`fix` 27、`chore` 10(3 筆標 `!`)、`docs` 7、`refactor` 2(1 筆標 `!`)、`style` 1。
- **現行 17 支的檢查結果**:17 支都通過,0 項不符,3 個候選請人判斷(`git-conventional-commit` 與 `plan-with-class-diagram` 各一份樣板的逐行比對沒有鑑別力;`skill-diagnose` 有一個以否定詞開頭的跳轉條件)。
- **兩份 Skill 目錄**:`.claude/skills/` 與 `.agents/skills/` 逐檔相同。
- **驗證狀態**:17 支的 `description` 都以「(未驗證)」結尾,包含 `skill-engineering` 與道館一的三支。

自己重跑(需要 [uv](https://docs.astral.sh/uv/)):

```bash
git clone https://github.com/AI-x-BDD/BDGG-Dev-Skills && cd BDGG-Dev-Skills
uv run .claude/skills/skill-conform/scripts/check_skills.py --skills .claude/skills    # 檢查 17 支
diff -r -x README.md .claude/skills .agents/skills && echo 一致                         # 兩份目錄
git log --oneline task1-v1..task2-v1 -- .claude/skills/trunk-based-development         # 某一支的優化歷程
```
