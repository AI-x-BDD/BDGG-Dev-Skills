---
name: data-plan
description: 要分析資料庫要存什麼、手上已經有功能規格或 plan.md 指派了資料庫這一步時,用這支 Skill 從需求與前一波的 API 規格盤點要持久化的實體,定下表、欄位、關聯與約束,交出通過驗證、可以直接交付的 DBML 檔;使用者提到資料庫設計、資料模型、資料表設計、schema、DBML、ER 圖、ERD、data model 時使用。
---

# SOP

## Phase 1: 盤點資料
1. Read **這次要分析的介面**:plan.md 的端點盤點與波段表裡指派給這次的那一步;若 plan.md 指派了這一步 → 跳至 Phase 1 Step 3。
2. Ask 問使用者**這次要分析的端點、介面與需求出處**。
3. Read **分析的依據**:spec.md、research.md、techstack.md,以及這一步的理由欄點名的前幾步產出。
4. Think **盤點要持久化的實體與狀態**:每個需求出處都要對到至少一張表。

## Phase 2: 寫出 DBML
1. Think 依 `rules/資料表-規範.md` **定下每張表的細節**:欄位、關聯、唯一性與狀態約束。
2. Write 依骨架 `templates/schema.dbml` 與範例 `templates/schema.example.dbml` 在 plan.md 的 Documentation 樹替這一步列的 `.dbml` 路徑(沒有 plan.md 時是 spec.md 旁的 `contracts/schema.dbml`)**寫出 DBML 檔**。
3. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_dbml.py --dbml <schema.dbml 的路徑> --plan <plan.md 的路徑> --spec <spec.md 的路徑> --step <S 編號>` **取得 DBML 的驗證結果**;若有不過 → 跳至 Phase 2 Step 2。
4. Report **交出 DBML 與待決問題**:拿不準、要使用者決定的事不在中途詢問,一起列在這裡。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 盤點資料"]
        P1S1["1. Read：這次要分析的介面"]
        G_P1S1_1{"plan.md 指派了這一步？"}
        P1S2["2. Ask：這次要分析的<br/>端點、介面與需求出處"]
        P1S3["3. Read：分析的依據"]
        P1S4["4. Think：盤點要持久化的實體與狀態"]
    end
    subgraph P2["Phase 2: 寫出 DBML"]
        P2S1["1. Think：定下每張表的細節"]
        P2S2["2. Write：寫出 DBML 檔"]
        P2S3["3. Delegate：取得 DBML 的驗證結果"]
        G_P2S3_1{"有不過？"}
        P2S4["4. Report：交出 DBML 與待決問題"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| P1S3
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> P1S4
    P1S4 --> P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> G_P2S3_1
    G_P2S3_1 -->|是| P2S2
    G_P2S3_1 -->|否| P2S4
    P2S4 --> End
```
</details>
