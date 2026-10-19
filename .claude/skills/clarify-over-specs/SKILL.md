---
name: clarify-over-specs
description: specify 交出 spec.md 之後、要在技術研究之前把規格裡的缺口問清楚時,用這支 Skill 逐個面向盤點 spec.md 的缺口,轉交 clarify 問答,把拍板的決策改寫進對應的章節並通過結構檢查,交出含覆蓋表的澄清報告;使用者提到澄清規格、規格有缺口、spec 審查、檢查 spec.md、clarify spec、speckit clarify 時使用。(未驗證)
---

# SOP

## Phase 1: 列出 spec.md 的缺口
1. Read **要澄清的 spec.md 與同資料夾的檔**:使用者沒有指定時,用 `specs/` 底下編號最大的資料夾。
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/constitution_rules.py --constitution <專案根目錄>/constitution --artifact specify/spec` **取得套用到 spec.md 的憲法條文**。
3. Think 依 `rules/缺口面向-規範.md` **列出每個面向的覆蓋狀況與缺口**;若每個面向都清楚 → 跳至 Phase 4 Step 1。

## Phase 2: 取得澄清結果
1. Delegate 轉交 clarify **取得這一場的澄清結果**:主題是這份 spec.md,指定的提問面向是 Phase 1 列出的缺口,附上前幾場已拍板的決策,只在對話裡交還。

## Phase 3: 改寫 spec.md
1. Write 依 `rules/spec改寫-規範.md` **把澄清結果改寫進 spec.md**:決策寫進對應的章節,問答追加到釐清紀錄。
2. Delegate 執行 `uv run scripts/check_spec.py --spec <spec.md 的路徑>` **取得 spec.md 的結構檢查結果**;若有不過 → 跳至 Phase 3 Step 1。
3. Think **逐條對照憲法的條文**;若有不過 → 跳至 Phase 3 Step 1;若剩餘的風險都不會改變規格 → 跳至 Phase 4 Step 1。
4. Ask **問使用者要不要再開一場**;若使用者要 → 跳至 Phase 2 Step 1。

## Phase 4: 交出澄清報告
1. Report 依骨架 `templates/澄清報告.md` 與範例 `templates/澄清報告.example.md` **交出澄清報告**:問了幾題、改了哪些章節、各面向的覆蓋狀況、交給技術研究的項目、編號的變動與下一步。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 列出 spec.md 的缺口"]
        P1S1["1. Read：要澄清的<br/>spec.md 與同資料夾的檔"]
        P1S2["2. Delegate：取得套用<br/>到 spec.md 的憲法條文"]
        P1S3["3. Think：列出每個面<br/>向的覆蓋狀況與缺口"]
        G_P1S3_1{"每個面向都清楚？"}
    end
    subgraph P2["Phase 2: 取得澄清結果"]
        P2S1["1. Delegate：取得這一場的澄清結果"]
    end
    subgraph P3["Phase 3: 改寫 spec.md"]
        P3S1["1. Write：把澄清結果改寫進 spec.md"]
        P3S2["2. Delegate：取得<br/>spec.md 的結構檢查結果"]
        G_P3S2_1{"有不過？"}
        P3S3["3. Think：逐條對照憲法的條文"]
        G_P3S3_1{"有不過？"}
        G_P3S3_2{"剩餘的風險都不<br/>會改變規格？"}
        P3S4["4. Ask：問使用者要不要再開一場"]
        G_P3S4_1{"使用者要？"}
    end
    subgraph P4["Phase 4: 交出澄清報告"]
        P4S1["1. Report：交出澄清報告"]
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> G_P1S3_1
    G_P1S3_1 -->|是| P4S1
    G_P1S3_1 -->|否| P2S1
    P2S1 --> P3S1
    P3S1 --> P3S2
    P3S2 --> G_P3S2_1
    G_P3S2_1 -->|是| P3S1
    G_P3S2_1 -->|否| P3S3
    P3S3 --> G_P3S3_1
    G_P3S3_1 -->|是| P3S1
    G_P3S3_1 -->|否| G_P3S3_2
    G_P3S3_2 -->|是| P4S1
    G_P3S3_2 -->|否| P3S4
    P3S4 --> G_P3S4_1
    G_P3S4_1 -->|是| P2S1
    G_P3S4_1 -->|否| P4S1
    P4S1 --> End
```

```mermaid
sequenceDiagram
    actor User
    participant Main as clarify-over-specs
    participant Sub_1 as clarify 取得這一場的澄清結果:主題是這份 spec.md
    Note over User,Sub_1: Phase 2: 取得澄清結果
    Main->>Sub_1: 1. Delegate：取得這一場的澄清結果
    Sub_1-->>Main: 完成並交回產出
    Note over User,Sub_1: Phase 3: 改寫 spec.md
    Main->>User: 4. Ask：問使用者要不要再開一場
    User-->>Main: 回覆確認
    Note over User,Sub_1: Phase 4: 交出澄清報告
    Main->>User: 1. Report：交出澄清報告
```
</details>
