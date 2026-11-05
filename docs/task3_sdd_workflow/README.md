# 作業三：SDD workflow 與五次作品迭代

本頁集中作業說明與證據入口。[題目原文](題目.md)、[結構檢視](review/結構檢視.md)與[歷史環境待辦](work-environment/tasks.md)各自保留;環境待辦不算本作業的產品需求。

## 第一題：主要 Skills

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

## 第二題：輔助 Skills

[constitution](../../.claude/skills/constitution/SKILL.md)、[clarify](../../.claude/skills/clarify/SKILL.md)與 [analyze](../../.claude/skills/analyze/SKILL.md)的實際問答回寫、跨檔問題修正與憲法使用證據見 [task2-evidence](task2-evidence/README.md)。[analyze-verify](analyze-verify/README.md)保留對照組與埋問題組。

## 第三題：watchlater-notes

作品：[GitHub 原始碼與執行方式](https://github.com/YongRui0402/watchlater-notes)、[開發與驗收紀錄](https://github.com/YongRui0402/watchlater-notes/blob/main/docs/development-record.md)、[公開歷史說明](https://github.com/YongRui0402/watchlater-notes/blob/main/docs/history.md)。這些證據不需要存取家庭內網的 GitLab。

相較 1A2B 即時對戰,本作品增加兩個面向的複雜度:

- **非同步與外部整合**：取得字幕、語音辨識、OCR、摘要、排程訂閱、取消與失敗處理要跨多種工具與服務,不是只處理同一局遊戲的即時訊息。
- **持久資料與編輯一致性**：影片、筆記、原始／編輯後文件、工作、標籤與替換紀錄需要共存;單處撤銷、錨點失效及跨筆記字彙必須維持資料一致性。

| 迭代 | 交付內容 | 公開規格與提交 |
|---|---|---|
| 001 | 影片逐字稿、筆記、匯出與訂閱 | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/001-video-notes-web)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/001-video-notes-web) |
| 002 | 拆分文件與模型設定 | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/002-split-docs-model-settings)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/002-split-docs-model-settings) |
| 003 | 擷取畫面文字 OCR | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/003-screen-text-ocr)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/003-screen-text-ocr) |
| 004 | 校正逐字稿與外部辨識時間點 | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/004-transcript-correction)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/004-transcript-correction) |
| 005 | 校正傳播、單處撤銷、標籤字彙與版本顯示 | [規格包](https://github.com/YongRui0402/watchlater-notes/tree/main/specs/005-correction-coverage)、[歷史](https://github.com/YongRui0402/watchlater-notes/commits/main/specs/005-correction-coverage) |

每包保留 spec、research、plan、tasks、analysis、合約與原型。公開歷史保留原有 143 個提交,另有一個公開文件整理提交;匿名化後 SHA 與私有原件不同。私人截圖不提供,文字驗收結論與未複核限制仍保留。

## 第四題：verify-plan

既有流程能規劃介面與任務,但缺少專門比較測試替身與真實元件差異的步驟,因此曾在最後瀏覽器驗收才發現導頁與 htmx 行為問題。

新增的 [verify-plan](../../.claude/skills/verify-plan/SKILL.md)放在 system-analysis 之後、tasks 之前,讀取規格與分析產出,寫出真實元件、替身、樣本、操作、通過條件與副作用邊界。tasks 納入每一項實跑任務,analyze 一併交叉檢查。

實際產出：[第五次迭代的 13 項驗收規劃](https://github.com/YongRui0402/watchlater-notes/blob/main/specs/005-correction-coverage/verify-plan.md)、[驗收結果與限制](https://github.com/YongRui0402/watchlater-notes/blob/main/specs/005-correction-coverage/research.md)。新增與優化的原因、預期、根因、修改與重跑結果保留在本 repo 的相關 commit 訊息。

## 繳交狀態

已有五次迭代與公開證據,尚未建立作業三繳交 tag,也尚未提供題目要求的一分鐘影片連結。格式檢查與既有實跑結果不等於所有 Skill 行為皆已驗證。
