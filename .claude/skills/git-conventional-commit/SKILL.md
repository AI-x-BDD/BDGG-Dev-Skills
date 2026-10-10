---
name: git-conventional-commit
description: 依 Conventional Commits 1.0.0 寫 git commit 訊息,並在提交前把不相關的變更拆成不同的 commit。只要準備執行 git commit、要寫或改寫 commit message、要決定 type 或 scope、要判斷是不是 breaking change、手上有一堆混在一起的 diff 要整理、要 revert / amend / squash,或使用者說「幫我 commit」「提交」「寫 commit 訊息」「切 commit」「commit 一下」,都先讀這支 skill —— 即使使用者完全沒提到 Conventional Commits 也一樣。(未驗證)
---

# SOP

## Phase 1: 提交 commit
1. Read **工作區與最近提交的現況**:`git status`、`git diff`、`git diff --staged` 與 `git log -n 15 --format='%h %s'` 的輸出。
2. Think 依 `rules/提交計畫-規範.md` 把這批變更**分成一筆一筆的 commit** 並排出提交的順序。
3. Write 依 `rules/index-規範.md` **把這一筆的變更 stage 進 index**;若這個 repo 沒有建置或測試指令 → 跳至 Phase 1 Step 5。
4. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/verify_staged.py --repo <repo 根目錄> --link <被 gitignore 的建置相依> --cmd <建置與測試指令>` **取得這一筆單獨取出時的建置結果**;若建置或測試失敗 → 跳至 Phase 1 Step 2。
5. Write 依 `rules/commit-message-規範.md`、骨架 `templates/commit-message.txt` 與範例 `templates/commit-message.example.txt` **把這一筆的 commit 訊息寫成訊息檔**。
6. Delegate 執行 `uv run scripts/check_commit_msg.py --file <訊息檔>` **取得訊息的檢查結果**;若有 ERROR → 跳至 Phase 1 Step 5。
7. Write 以 `git commit -F <訊息檔>` **提交這一筆**;若還有下一筆 → 跳至 Phase 1 Step 3。

## Phase 2: 列出回報
1. Think 依 `rules/回報-規範.md`、骨架 `templates/回報.md` 與範例 `templates/回報.example.md` **列出這次提交的回報**。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 提交 commit"]
        P1S1["1. Read：工作區與最近提交的現況"]
        P1S2["2. Think：分成一筆一筆的 commit"]
        P1S3["3. Write：把這一筆的<br/>變更 stage 進 index"]
        G_P1S3_1{"這個 repo 沒有建<br/>置或測試指令？"}
        P1S4["4. Delegate：取得這一<br/>筆單獨取出時的建置結果"]
        G_P1S4_1{"建置或測試失敗？"}
        P1S5["5. Write：把這一筆的<br/>commit 訊息寫成訊息檔"]
        P1S6["6. Delegate：取得訊息的檢查結果"]
        G_P1S6_1{"有 ERROR？"}
        P1S7["7. Write：提交這一筆"]
        G_P1S7_1{"還有下一筆？"}
    end
    subgraph P2["Phase 2: 列出回報"]
        P2S1["1. Think：列出這次提交的回報"]
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| P1S5
    G_P1S3_1 -->|否| P1S4
    P1S4 --> G_P1S4_1
    G_P1S4_1 -->|是| P1S2
    G_P1S4_1 -->|否| P1S5
    P1S5 --> P1S6
    P1S6 --> G_P1S6_1
    G_P1S6_1 -->|是| P1S5
    G_P1S6_1 -->|否| P1S7
    P1S7 --> G_P1S7_1
    G_P1S7_1 -->|是| P1S3
    G_P1S7_1 -->|否| P2S1
    P2S1 --> End
```
</details>
