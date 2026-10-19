---
name: api-plan
description: 要分析後端對外的 API(REST、WebSocket 訊息協定,或從 API 角度看第三方服務的介面)、手上已經有功能規格或 plan.md 指派了這一步時,用這支 Skill 從需求盤點操作與事件,交出通過驗證、可以直接交付的 OpenAPI 與 AsyncAPI 規格檔;使用者提到 API 設計、API 規劃、API contract、OpenAPI、Swagger、AsyncAPI、WebSocket 協定、訊息協定、REST API、endpoint 時使用。
---

# SOP

## Phase 1: 盤點操作
1. Read **這次要分析的介面**:plan.md 的端點盤點與波段表裡指派給這次的那一步;若 plan.md 指派了這一步 → 跳至 Phase 1 Step 3。
2. Ask 問使用者**這次要分析的端點、介面與需求出處**。
3. Read **分析的依據**:spec.md、research.md、techstack.md,以及這一步的理由欄點名的前幾步產出。
4. Think **盤點這個介面的操作與事件**:每個需求出處都要對到至少一個操作或事件。

## Phase 2: 寫出規格檔
1. Think 依 `rules/契約-規範.md` **定下每個操作的細節**:請求、回應、錯誤與推送對象;若這個介面沒有 request/response 的操作 → 跳至 Phase 2 Step 3。
2. Write 依骨架 `templates/openapi.yaml` 與範例 `templates/openapi.example.yaml` 在 plan.md 的 Documentation 樹替這一步列的 `.openapi.yaml` 路徑(沒有 plan.md 時是 spec.md 旁的 `contracts/openapi.yaml`)**寫出 OpenAPI 檔**;若這個介面沒有推送的操作 → 跳至 Phase 2 Step 4。
3. Write 依骨架 `templates/asyncapi.yaml` 與範例 `templates/asyncapi.example.yaml` 在 plan.md 的 Documentation 樹替這一步列的 `.asyncapi.yaml` 路徑(沒有 plan.md 時是 spec.md 旁的 `contracts/asyncapi.yaml`)**寫出 AsyncAPI 檔**。
4. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_api.py --openapi <openapi.yaml 的路徑> --asyncapi <asyncapi.yaml 的路徑> --plan <plan.md 的路徑> --spec <spec.md 的路徑> --step <S 編號>` **取得規格檔的驗證結果**:沒寫的那一份省略它的參數;若有不過 → 跳至 Phase 2 Step 1。
5. Report **交出規格檔與待決問題**:拿不準、要使用者決定的事不在中途詢問,一起列在這裡。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 盤點操作"]
        P1S1["1. Read：這次要分析的介面"]
        G_P1S1_1{"plan.md 指派了這一步？"}
        P1S2["2. Ask：這次要分析的<br/>端點、介面與需求出處"]
        P1S3["3. Read：分析的依據"]
        P1S4["4. Think：盤點這個介面的操作與事件"]
    end
    subgraph P2["Phase 2: 寫出規格檔"]
        P2S1["1. Think：定下每個操作的細節"]
        G_P2S1_1{"這個介面沒有<br/>request/response<br/>的操作？"}
        P2S2["2. Write：寫出 OpenAPI 檔"]
        G_P2S2_1{"這個介面沒有推送的操作？"}
        P2S3["3. Write：寫出 AsyncAPI 檔"]
        P2S4["4. Delegate：取得規格檔的驗證結果"]
        G_P2S4_1{"有不過？"}
        P2S5["5. Report：交出規格檔與待決問題"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| P1S3
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> P1S4
    P1S4 --> P2S1
    P2S1 --> G_P2S1_1
    G_P2S1_1 -->|是| P2S3
    G_P2S1_1 -->|否| P2S2
    P2S2 --> G_P2S2_1
    G_P2S2_1 -->|是| P2S4
    G_P2S2_1 -->|否| P2S3
    P2S3 --> P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P2S1
    G_P2S4_1 -->|否| P2S5
    P2S5 --> End
```
</details>
