---
name: specify
description: 要把一段功能描述寫成功能規格、開始做一個新功能之前,用這支 Skill 釐清需求、切出使用者故事並把 FR 與 NFR 歸到故事底下,交出通過結構檢查的 spec.md;使用者提到 specify、speckit、spec-kit、寫規格、功能規格、需求規格、spec.md、user story、使用者故事時使用。(未驗證)
---

# SOP

## Phase 1: 建立規格資料夾
1. Read **使用者的功能描述**。
2. Think **決定功能簡稱**:2 到 4 個英文單字的 kebab-case。
3. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/create_feature.py --short-name <功能簡稱>` **建立規格資料夾**。

## Phase 2: 釐清需求
1. Think 依 `rules/釐清-規範.md` **列出功能描述裡會影響範圍的不確定處**。
2. Ask **一次問一題不確定處**並記下回答;若還有影響範圍的不確定處 → 跳至 Phase 2 Step 2。

## Phase 3: 寫出規格
1. Think **切出使用者故事**:每個故事可獨立測試,並排出優先順序。
2. Think 依 `rules/需求歸屬-規範.md` **歸屬每條 FR 與 NFR**:放進所屬的使用者故事或全域需求。
3. Write 依骨架 `templates/spec.template.md` 與範例 `templates/spec.template.example.md` **寫出 spec.md**。

## Phase 4: 驗收規格
1. Delegate 執行 `uv run scripts/check_spec.py --spec <spec.md 的路徑>` **取得 spec.md 的結構檢查結果**;若有不過 → 跳至 Phase 3 Step 3。
2. Think **逐條對照腳本沒有判的 Rule**;若有不過 → 跳至 Phase 3 Step 2。
3. Ask **提出規格摘要**,問使用者是否同意;若出現新的不確定處 → 跳至 Phase 2 Step 2;若使用者要修改 → 跳至 Phase 3 Step 1。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 建立規格資料夾"]
        P1S1["1. Read：使用者的功能描述"]
        P1S2["2. Think：決定功能簡稱"]
        P1S3["3. Delegate：建立規格資料夾"]
    end
    subgraph P2["Phase 2: 釐清需求"]
        P2S1["1. Think：列出功能描述<br/>裡會影響範圍的不確定處"]
        P2S2["2. Ask：一次問一題不確定處"]
        G_P2S2_1{"還有影響範圍的不確定處？"}
    end
    subgraph P3["Phase 3: 寫出規格"]
        P3S1["1. Think：切出使用者故事"]
        P3S2["2. Think：歸屬每條 FR 與 NFR"]
        P3S3["3. Write：寫出 spec.md"]
    end
    subgraph P4["Phase 4: 驗收規格"]
        P4S1["1. Delegate：取得<br/>spec.md 的結構檢查結果"]
        G_P4S1_1{"有不過？"}
        P4S2["2. Think：逐條對照腳本沒有判的 Rule"]
        G_P4S2_1{"有不過？"}
        P4S3["3. Ask：提出規格摘要"]
        G_P4S3_1{"出現新的不確定處？"}
        G_P4S3_2{"使用者要修改？"}
    end
    End["結束"]
    P1S1 --> P1S2
    P1S2 --> P1S3
    P1S3 --> P2S1
    P2S1 --> P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P2S2
    G_P2S2_1 -->|否| P3S1
    P3S1 --> P3S2
    P3S2 --> P3S3
    P3S3 --> P4S1
    P4S1 --> G_P4S1_1
    G_P4S1_1 -->|是| P3S3
    G_P4S1_1 -->|否| P4S2
    P4S2 --> G_P4S2_1
    G_P4S2_1 -->|是| P3S2
    G_P4S2_1 -->|否| P4S3
    P4S3 --> G_P4S3_1
    G_P4S3_1 -->|是| P2S2
    G_P4S3_1 -->|否| G_P4S3_2
    G_P4S3_2 -->|是| P3S1
    G_P4S3_2 -->|否| End
```
</details>
