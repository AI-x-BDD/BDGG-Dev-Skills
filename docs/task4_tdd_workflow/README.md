# 道館四:AI x TDD Workflow

[題目原文](題目.md)。繳交版本:tag [`task4-v1`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/task4-v1);這座道館的全部變更:[`task3-v1...task4-v1`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/compare/task3-v1...task4-v1)。作品是 [colab-gpu-bridge](https://github.com/YongRui0402/colab-gpu-bridge)(用 Colab 的 GPU 跑 Ollama,從區網呼叫;執行方式見其 README),跑了三次迭代(001~003)。

## 完成條件

| 題目要的 | 位置 |
|---|---|
| 第一題 Workflow 的 Skill packages 與使用順序 | [第一題](#第一題workflow) |
| 第二題作品原始碼、執行方式、測試計畫、任務與測試結果 | [第二題](#第二題colab-gpu-bridge) |
| 第三題改寫的 Skill、改寫部位與實際結果 | [第三題](#第三題改進) |
| 第三題客製化說明 | [第三題](#第三題改進) |
| 一分鐘介紹影片 | 另行提供 |

## 第一題:Workflow

```text
specify → clarify-over-specs → technical-research → system-analysis → testplan → tasks → analyze → implement
                                                      ├ api-plan                                        └ tdd(紅燈/綠燈/重構)
                                                      ├ data-plan
                                                      ├ ui-plan
                                                      └ deploy-plan
```

- [testplan](../../.claude/skills/testplan/SKILL.md) 依端點與使用者故事寫出假如/當/則的案例,交給 [tasks](../../.claude/skills/tasks/SKILL.md)。
- tasks 每個案例排一組紅燈、綠燈任務,每節一個重構任務,量測案例一個 📏 任務。
- [implement](../../.claude/skills/implement/SKILL.md) 逐任務呼叫 [tdd](../../.claude/skills/tdd/SKILL.md) 只做指定的那一步;每個 phase 的 Checkpoint 跑完整驗收。

## 第二題:colab-gpu-bridge

| 迭代 | 範圍 | 測試計畫 · 任務 · 結果 |
|---|---|---|
| 001 | 工作階段管理與模型目錄(全端) | 538 任務;8 條 SC 以真的 Colab T4 實跑達標 |
| 002 | 官方模型庫的錯誤處理 | 168 任務;662 passed |
| 003 | 下載去重、模型目錄快取 | 131 任務;748 passed;[耗時與用量](#第三題改進) |

每次迭代的 `specs/00N-*/` 裡有 testplan.md、tasks.md 與完成報告。

作品 repo:[YongRui0402/colab-gpu-bridge](https://github.com/YongRui0402/colab-gpu-bridge)。各迭代的規格、testplan、tasks 與完成報告:[001](https://github.com/YongRui0402/colab-gpu-bridge/tree/main/specs/001-session-model-catalog)、[002](https://github.com/YongRui0402/colab-gpu-bridge/tree/main/specs/002-library-error-handling)、[003](https://github.com/YongRui0402/colab-gpu-bridge/tree/main/specs/003-download-dedup-model-cache);第三題引用的[觀察紀錄](https://github.com/YongRui0402/colab-gpu-bridge/blob/main/docs/觀察紀錄.md)與[耗時紀錄](https://github.com/YongRui0402/colab-gpu-bridge/blob/main/docs/耗時與用量紀錄-003.md)。

## 第三題:改進

從第二題的觀察紀錄(70 條)挑出問題,改寫 testplan、tdd、tasks、implement 與決定規範,**不新增 Skill**。對照課程版 `CH4-SDD-TDD-workflow/skills`(367d75a,課程 repo 僅限學員):下面三組共 12 項改動,10 項課程沒有,2 項(★)是在課程基礎上加嚴。

### 1. 測試計畫要逼出「替身驗不到的錯」

| | |
|---|---|
| 問題 | 001 用替身的 574 個測試全綠,第一次實跑就抓到 4 個錯;合約有的錯誤碼沒有案例,TDD 的「最少程式」把它們做掉了 |
| 改動 | testplan:每個替身指到一個 📏 實跑案例(寫護欄與判定者);覆蓋檢查對照合約錯誤碼;實跑標時機(節內/整合);分層測試指令。腳本 `check_testplan.py` 擋 |
| 結果 | 002、003 的實跑案例都有護欄與判定者;003 的 testplan 主 agent 輸出 271k → 87k(端點節平行寫成檔再拼接) |
| 弱項 | 實跑判定仍要人或腳本看數字;「替身要實跑」源自作業三的 verify-plan,本館是把它內化進 testplan |

### 2. TDD 要快,紅燈也要可信

| | |
|---|---|
| 問題 | 002 故事 1 的 95 個任務做了約 2 小時,61% 在等測試;許多紅燈「一寫就綠」,說不出測試抓不抓得到錯 |
| 改動 | ★tdd 測試範圍分層(紅燈只跑那一支、綠燈跑任務的測試檔);★implement 每個端點一個 worktree、Sonnet 平行、合併後只在 Checkpoint 跑一次全部;已被滿足的案例,tasks 預先寫成**對照組紅燈**(暫時放入錯誤實作、確認斷言失敗) |
| 結果 | 003 故事 1 的 91 個任務 51 分鐘;45 個對照組紅燈預先寫好,故事 1 的 31 個預測 0 個失準 |
| 弱項 | 對照組改壞的方式偶爾做錯(131 任務中 2 次,觀察紀錄 #67、#68) |

### 3. 決定不能互相矛盾,也不能忘記上一次迭代

| | |
|---|---|
| 問題 | 003 的 testplan 決定讓實跑打桌機的 Ollama,違反 001 的護欄;只靠 analyze 追原始碼才攔下 |
| 改動 | 決定規範:寫回前對照 spec、規格檔、先前決定與**前面迭代的實跑護欄**,改判新增取代列;實作中途補案例時回 testplan、tasks,既有任務編號不動;`check_plan` 沿著迭代鏈判定端點編號;只改文件的 commit 不跑測試 |
| 結果 | 用 skill-diagnose 做切片 A/B 實驗確診,三個根因修完後以不帶脈絡的 subagent 驗收,4 列都對得上 |
| 弱項 | agent 研究時順手跑的指令不經過規範,另寫進作品的 `CLAUDE.md` |

### 和 TDD、可靠度的關係

- **測什麼**:案例由規格與合約推出,替身一定配實跑,「全綠但錯」少一層。
- **紅燈可信**:沒有斷言失敗的紅燈不算數,已被滿足的案例用對照組證明測試抓得到錯。
- **回饋要快**:測試範圍分層、平行實作,紅綠循環不被等測試拖慢。

### 自我檢查(題目引導的五個問題)

| 問題 | 回答 | 證據 |
|---|---|---|
| AI 還要自己猜嗎? | 仍會遇到規格沒寫的細節,但不再默默猜:端點節把它們登記成待決問題,決定後才寫測試 | 003 testplan 登記 Q7~Q22 共 16 題 |
| 換新對話還做得到嗎? | 可以。003 每個階段都交給不帶脈絡的 subagent,只讀 spec package 就完成;漏的是前一次迭代的護欄,已補進決定規範 | 觀察紀錄 #59;CH4 [`9f812a3`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/9f812a3) |
| 測試通過 = 功能做到了嗎? | 不一定。001 替身全綠,實跑才抓到 4 個錯;003 全綠,上 Tower 第一次使用就發現「結束後不能再開」(testplan 沒有這個案例) | 觀察紀錄 #41、#42、#71 |
| 這次成功,哪些是 AI 自己想到的? | clarify 自己讀前一次的合約抓到 null 的矛盾、analyze 自己追原始碼抓到護欄衝突;後者已寫進 skill | 觀察紀錄 #46、#59 |
| 改進真的有幫助嗎? | 實作變快、紅燈可信;規劃變慢。也刪掉了重複:verify-plan 退場,併進 testplan | 下表;CH4 [`cc8a49f`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/commit/cc8a49f) |

### 實際結果(003 和 002 比)

| 指標 | 002 | 003 |
|---|---|---|
| 規劃(specify → analyze) | 54 分 | 109 分(22 分在等只改文件的 commit 跑測試,已修) |
| implement 每任務 | 0.51 分 | 0.66 分 |
| analyze | — | 第 1 輪攔下 2 個決定矛盾,第 2 輪通過 |

規劃變慢是這次的代價:多了 clarify-over-specs 與 analyze 回修。細節在作品 repo 的[耗時紀錄](https://github.com/YongRui0402/colab-gpu-bridge/blob/main/docs/耗時與用量紀錄-003.md)。
