---
name: invoke-agy
description: 只要準備在指令列執行 `agy -p` 或 `agy --print`,不論是委派開發、重構、探索,還是拿 agy 當 subagent 做驗收實跑、審查或第二意見,都先用這支 Skill 組裝任務指示、以非互動模式調用、判定調用有沒有中斷並驗收結果;別支 Skill 的某一步要交給 agy 時也一樣;使用者提到調用 agy、呼叫 agy、叫 agy、委派 agy、用 agy 跑、用 agy 測試、用 agy 驗收、run agy、invoke agy、antigravity cli、叫 agy 做事時使用。(未驗證)
---

# SOP

## Phase 1: 產生任務指示檔
1. Read 使用者的委派任務需求、當前工作目錄與 git 狀態;若 agy 未安裝或環境不支援 → 結束。
2. Write 依骨架 `templates/task-prompt.md` 與範例 `templates/task-prompt.example.md` 把任務背景、修改範圍、操作限制與預期產出寫成任務指示檔。

## Phase 2: 判定調用結果
1. Think 依 `rules/調用-規範.md` 決定非互動調用參數與授權權限。
2. Delegate 執行 agy --print 指令傳入任務指示檔並將最後輸出寫入紀錄檔。
3. Read AGY 執行紀錄與工作目錄的 git diff。
4. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/judge_invocation.py --json <JSON 紀錄檔> --stderr <stderr 紀錄檔> --exit <結束碼紀錄檔>` 判定這次調用是成功、逾時、權限中止、額度用完或其他失敗;若判定不是成功 → 跳至 Phase 3 Step 2。

## Phase 3: 驗收成果並回報變更
1. Think 對照任務指示檔的驗收條件判定是否通過;若結果不符預期且需要 AGY 修正,而這次還沒有修正過 → 跳至 Phase 1 Step 2。
2. Ask 向使用者回報執行結果、變更內容與驗收依據。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 產生任務指示檔"]
        P1S1["1. Read：使用者的委派任務需<br/>求、當前工作目錄與 git 狀態"]
        G_P1S1_1{"未安裝或不支援？"}
        P1S2["2. Write：把任務背景、修改範圍、<br/>操作限制與預期產出寫成任務指示檔"]
    end
    subgraph P2["Phase 2: 判定調用結果"]
        P2S1["1. Think：決定非互動<br/>調用參數與授權權限"]
        P2S2["2. Delegate：執行 agy"]
        P2S3["3. Read：AGY 執行紀錄<br/>與工作目錄的 git diff"]
        P2S4["4. Delegate：判定這次調用是成功、<br/>逾時、權限中止、額度用完或其他失敗"]
        G_P2S4_1{"判定不是成功？"}
    end
    subgraph P3["Phase 3: 驗收成果並回報變更"]
        P3S1["1. Think：對照任務指示檔<br/>的驗收條件判定是否通過"]
        G_P3S1_1{"驗收不符預期？"}
        P3S2["2. Ask：向使用者回報執行<br/>結果、變更內容與驗收依據"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| End
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P3S2
    G_P2S4_1 -->|否| P3S1
    P3S1 --> G_P3S1_1
    G_P3S1_1 -->|是| P1S2
    G_P3S1_1 -->|否| P3S2
    P3S2 --> End
```
</details>
