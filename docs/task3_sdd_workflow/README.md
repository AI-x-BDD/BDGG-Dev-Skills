# 道館:SDD workflow、五次作品迭代與新 Skill

本頁集中作業說明與公開證據入口。[題目原文](題目.md)另行保留;家庭環境待辦與私有維運檢視不隨公開課程 repo 同步。

繳交版本:tag [`task3-v1`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/tree/task3-v1)。這座道館的全部變更:[`task2-v1...task3-v1`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/compare/task2-v1...task3-v1)。

## 完成條件

| 題目要的 | 位置 |
|---|---|
| 第一題八支主要 Skills 的完整 Skill packages | [第一題](#第一題主要-skills) |
| 第二題三支輔助 Skills 的完整 Skill packages | [第二題](#第二題輔助-skills) |
| 第三題前後端系統的原始碼與執行方式 | [watchlater-notes](https://github.com/YongRui0402/watchlater-notes)(執行方式見其 README) |
| 5～10 次完整 SDD workflow 迭代紀錄 | [第三題](#第三題watchlater-notes)的五次迭代表 |
| 使用 `/skill-engineering` 優化 Skills 的紀錄與 git commits | [`task2-v1...task3-v1`](https://github.com/AI-x-BDD/BDGG-Dev-Skills/compare/task2-v1...task3-v1);每個優化 commit 的訊息寫了問題、預期、根因、修改部位與再跑結果 |
| SDD workflow 優化紀錄 | [SDD 流程不足與已試過的優化](#sdd-流程不足與已試過的優化) |
| 第四題新 Skill 的完整 Skill package、加入位置與實際執行結果 | [第四題](#第四題verify-plan) |
| 一分鐘介紹影片 | 另行提供 |

## 第一題:主要 Skills

```text
specify → technical-research → system-analysis → verify-plan → tasks → analyze → implement
                                 ├ api-plan
                                 ├ data-plan
                                 ├ ui-plan
                                 └ deploy-plan
```

題目要求的八支 Skills:

| 職責 | Skill |
|---|---|
| 需求規格 | [specify](../../.claude/skills/specify/SKILL.md) |
| 技術研究 | [technical-research](../../.claude/skills/technical-research/SKILL.md) |
| 系統分析與 Planner 調度 | [system-analysis](../../.claude/skills/system-analysis/SKILL.md) |
| API、資料與 UI 規劃 | [api-plan](../../.claude/skills/api-plan/SKILL.md)、[data-plan](../../.claude/skills/data-plan/SKILL.md)、[ui-plan](../../.claude/skills/ui-plan/SKILL.md) |
| 任務拆解 | [tasks](../../.claude/skills/tasks/SKILL.md) |
| 實作 | [implement](../../.claude/skills/implement/SKILL.md) |

[deploy-plan](../../.claude/skills/deploy-plan/SKILL.md)補部署介面。[verify-plan](../../.claude/skills/verify-plan/SKILL.md)是第四題新增的真實環境驗收規劃。

## 第二題:輔助 Skills

[constitution](../../.claude/skills/constitution/SKILL.md)、[clarify](../../.claude/skills/clarify/SKILL.md)與 [analyze](../../.claude/skills/analyze/SKILL.md)的實際問答回寫、跨檔問題修正與憲法使用證據見 [task2-evidence](task2-evidence/README.md)。[analyze-verify](analyze-verify/README.md)保留對照組與埋問題組。

## 第三題:watchlater-notes

作品:[GitHub 原始碼與執行方式](https://github.com/YongRui0402/watchlater-notes)、[開發與驗收紀錄](https://github.com/YongRui0402/watchlater-notes/blob/main/docs/development-record.md)、[公開歷史說明](https://github.com/YongRui0402/watchlater-notes/blob/main/docs/history.md)。這些證據不需要存取家庭內網的 GitLab。

相較 1A2B 即時對戰,本作品增加兩個面向的複雜度:

- **非同步與外部整合**:取得字幕、語音辨識、OCR、摘要、排程訂閱、取消與失敗處理要跨多種工具與服務,不是只處理同一局遊戲的即時訊息。
- **持久資料與編輯一致性**:影片、筆記、原始／編輯後文件、工作、標籤與替換紀錄需要共存;單處撤銷、錨點失效及跨筆記字彙必須維持資料一致性。

| 迭代 | 交付內容 | 公開規格與提交 |
|---|---|---|
| 001 | 影片逐字稿、筆記、匯出與訂閱 | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/001-video-notes-web)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/001-video-notes-web) |
| 002 | 拆分文件與模型設定 | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/002-split-docs-model-settings)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/002-split-docs-model-settings) |
| 003 | 擷取畫面文字 OCR | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/003-screen-text-ocr)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/003-screen-text-ocr) |
| 004 | 校正逐字稿與外部辨識時間點 | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/004-transcript-correction)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/004-transcript-correction) |
| 005 | 校正傳播、單處撤銷、標籤字彙與版本顯示 | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/005-correction-coverage)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/005-correction-coverage) |

每包保留 spec、research、plan、tasks、analysis、合約與原型。公開歷史保留原有 143 個提交,另有一個公開文件整理提交;匿名化後 SHA 與私有原件不同。私人截圖不提供,文字驗收結論與未複核限制仍保留。

### SDD 流程不足與已試過的優化

以下依五次迭代實際遇到的問題整理,括號內是本 repo 對應的 commit 標題;每個 commit 訊息都寫了問題、預期、根因、修改部位與再跑結果。

| 步驟 | 不足之處 | 造成的影響 | 已試過的優化 |
|---|---|---|---|
| specify | 一輪只問一題;規格寫完後沒有正式的改需求入口 | 001 使用者要求「一次多問幾題」;003 研究途中改兩次需求只能手改 spec.md | 一輪問 1 到 4 題(`fix(specify): 釐清需求改成一輪問 1 到 4 題`);研究中途可回 specify 修改,不重排編號(`fix(specify,technical-research): 研究中途改需求有路可走…`) |
| technical-research | 證據規則只管「怎麼標示」,不管樣本怎麼取、看多少、何時停;方案依賴的事實可以沒有證據 | 002 R4 依賴兩個未驗證的 SDK 行為;003 用合成字幕的彙總數字定門檻,實作後字時有時無;探針跑 17 分鐘仍在多標影片;004 規則只在調整用樣本上看似零誤改 | 依賴的事實要回頭取證;探針先看一筆真實樣本、限時跑最小組合;定門檻前看逐筆輸出;留一份沒看過的樣本驗收,並在列研究項前寫分配表;再多一批不改決策就停;spec 對既有資料的假設先查一筆真實的;選型要對照同類產品 |
| system-analysis | 波段排法、重做範圍與委派指示的欄位沒有界線 | 001 前後端同一波各自定頁面,後端重做;重做一步後依賴它的步驟沒跟著重做,到 analyze 才發現;002 同一波兩個 api-plan 各取一套錯誤碼;003 planner 先採用與 spec 矛盾的做法 | 伺服器端渲染時前端排在後端下一波;重做時連帶重做下游;同一波共用約定、增量迭代沿用端點編號;委派指示一律列出要照的已決定題;和 spec 矛盾的做法不算先採用 |
| api-plan、ui-plan | 合約與原型的檢查不涵蓋外部命令列與欄位來源 | 001 `x-argv` 照抄進 shell 會失效、檢查腳本把 301 當失敗;002 原型顯示 4 個 API 沒有的欄位 | 外部命令列寫成可直接貼進 shell 的形式;3xx 視為成功;畫面欄位要對得到前幾步的產出 |
| tasks | 任務只從介面元素出發,背景流程、膠水檔、新增列舉值、SC 的量測與真瀏覽器驗收都沒有任務 | 001 漏掉上傳來源的整理流程;003 新增 `RUNNING` 漏了 `UNFINISHED`,工作不能取消;004 自動測試全綠,工作列表點不進舊工作到最後瀏覽器實測才發現 | 驗收情境經過的每段處理都要有任務;膠水檔與被取代的舊測試要有任務;新增列舉值時搜同一概念的每份清單;每條 SC 要有量測任務;含畫面的故事要有真瀏覽器任務;DBML 改用 pydbml 解析 |
| analyze | 前置檢查沒有考慮增量迭代 | 003 對增量 plan.md 兩輪都報端點編號不連號的假警報 | 把前一次迭代的 plan.md 轉交給 check_plan |
| implement | 平行 subagent 之間沒有共用規格錨點,subagent 可改動 git index | 001 主 agent 自補的介面約定和 DBML 路徑基準不一致;002 一個 subagent 的 `git rm` 被另一組的 commit 帶走 | 端點指示列出跨端點要照的規格錨點;禁止 subagent stage;每個 phase 一併檢查 plan.md 待決問題格式 |

最大的缺口是「測試替身和真實元件的落差沒有人負責」:訂閱 bug 靠假 yt-dlp 過關,004 的導頁與 htmx 問題到最後才發現。逐條補 tasks 規則只能治標,因此第四題新增 verify-plan,在進 tasks 之前專門規劃真實環境驗收。

仍有的限制:檢查腳本多數只驗結構與覆蓋,不驗內容是否正確;部分再跑結果由不帶脈絡的 subagent 回報,只抽查了一部分。

## 第四題:verify-plan

既有流程能規劃介面與任務,但缺少專門比較測試替身與真實元件差異的步驟,因此曾在最後瀏覽器驗收才發現導頁與 htmx 行為問題。

新增的 [verify-plan](../../.claude/skills/verify-plan/SKILL.md)放在 system-analysis 之後、tasks 之前,讀取規格與分析產出,寫出真實元件、替身、樣本、操作、通過條件與副作用邊界。tasks 納入每一項實跑任務,analyze 一併交叉檢查。

實際產出:[第五次迭代的 13 項驗收規劃](https://github.com/YongRui0402/watchlater-notes/blob/main/specs/005-correction-coverage/verify-plan.md)、[驗收結果與限制](https://github.com/YongRui0402/watchlater-notes/blob/main/specs/005-correction-coverage/research.md)。新增與優化的原因、預期、根因、修改與重跑結果保留在本 repo 的相關 commit 訊息。

## 驗證狀態

各支的 `description` 仍標示「(未驗證)」。格式檢查與既有實跑結果不等於所有 Skill 行為皆已驗證。
