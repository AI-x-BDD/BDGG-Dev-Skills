---
name: invoke-agy
description: 需要將開發、重構、架構設計或探索任務委派給 Antigravity CLI (agy) 執行時,用這支 Skill 進行環境檢查、組裝任務指示、以非互動模式調用並驗收結果;使用者提到調用 agy、呼叫 agy、叫 agy、委派 agy、run agy、invoke agy、antigravity cli、叫 agy 做事時使用。(未驗證)
---

# SOP

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 確認前置檢查紀錄"]
        P1S1["1. Read：使用者的委派任務需求、當前工作目錄與 git 狀態"]
        G_P1S1_1{"未安裝或不支援？"}
        P1S2["2. Think：整理任務邊界、目標修改檔案與目前的 git baseline"]
    end
    subgraph P2["Phase 2: 產生任務指示檔"]
        P2S1["1. Think：規劃任務指示的內容結構與約束條件"]
        P2S2["2. Write：把任務背景、修改範圍、操作限制與預期產出寫成任務指示檔"]
    end
    subgraph P3["Phase 3: 執行調用並記錄結果"]
        P3S1["1. Think：決定非互動調用參數與授權權限"]
        P3S2["2. Delegate：執行 agy"]
        G_P3S2_1{"調用失敗？"}
    end
    subgraph P4["Phase 4: 驗收成果並回報變更"]
        P4S1["1. Read：AGY 執行紀錄與工作目錄的 git diff"]
        P4S2["2. Think：對照任務指示檔的驗收條件判定是否通過"]
        G_P4S2_1{"驗收不符預期？"}
        P4S3["3. Ask：向使用者回報執行結果、變更內容與驗收依據"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| End
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P2S1
    P2S1 --> P2S2
    P2S2 --> P3S1
    P3S1 --> P3S2
    P3S2 --> G_P3S2_1
    G_P3S2_1 -->|是| P3S1
    G_P3S2_1 -->|否| P4S1
    P4S1 --> P4S2
    P4S2 --> G_P4S2_1
    G_P4S2_1 -->|是| P2S1
    G_P4S2_1 -->|否| P4S3
    P4S3 --> End
```
</details>

## Phase 1: 確認前置檢查紀錄
1. Read 使用者的委派任務需求、當前工作目錄與 git 狀態;若 agy 未安裝或環境不支援 → 結束。
2. Think 整理任務邊界、目標修改檔案與目前的 git baseline。

## Phase 2: 產生任務指示檔
1. Think 規劃任務指示的內容結構與約束條件。
2. Write 依骨架 `templates/task-prompt.md` 與範例 `templates/task-prompt.example.md` 把任務背景、修改範圍、操作限制與預期產出寫成任務指示檔。

## Phase 3: 執行調用並記錄結果
1. Think 依 `rules/調用-規範.md` 決定非互動調用參數與授權權限。
2. Delegate 執行 agy --print 指令傳入任務指示檔並將最後輸出寫入紀錄檔;若調用失敗 → 跳至 Phase 3 Step 1。

## Phase 4: 驗收成果並回報變更
1. Read AGY 執行紀錄與工作目錄的 git diff。
2. Think 對照任務指示檔的驗收條件判定是否通過;若結果不符預期且需要 AGY 修正 → 跳至 Phase 2 Step 1。
3. Ask 向使用者回報執行結果、變更內容與驗收依據。
