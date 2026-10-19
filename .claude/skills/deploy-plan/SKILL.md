---
name: deploy-plan
description: 要分析這個功能怎麼部署、對外開哪些 port 與路徑,手上已經有功能規格或 plan.md 指派了部署這一步時,用這支 Skill 從需求與前幾步的規格檔盤點要跑的服務、對外入口與要掛載的檔案,交出通過驗證、可以直接交付的 compose.yaml 與它用到的 Dockerfile、.env.example、反向代理設定;使用者提到部署、deploy、docker compose、compose.yaml、Dockerfile、反向代理、reverse proxy、port、上線時使用。(未驗證)
---

# SOP

## Phase 1: 盤點部署需求
1. Read **這次要分析的介面**:plan.md 的端點盤點與波段表裡指派給這次的那一步;若 plan.md 指派了這一步 → 跳至 Phase 1 Step 3。
2. Ask 問使用者**這次要分析的端點、介面與需求出處**。
3. Read **分析的依據**:spec.md、research.md、techstack.md,以及這一步的理由欄點名的前幾步產出。
4. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/constitution_rules.py --constitution <專案根目錄>/constitution --artifact deploy-plan/compose` **取得套用到部署檔的憲法條文**。
5. Think **盤點要跑的服務與對外入口**:每個需求出處都要對到至少一個服務。

## Phase 2: 寫出部署檔
1. Think 依 `rules/部署-規範.md` **定下每個服務的細節**:image、port、volume、環境變數與健康檢查。
2. Write 依骨架 `templates/compose.yaml` 與範例 `templates/compose.example.yaml` 在 plan.md 的 Documentation 樹替這一步列的資料夾(沒有 plan.md 時是 spec.md 旁的 `deploy/`)**寫出 `compose.yaml`**:前幾步已經寫過的就接著改。
3. Write 在同一個資料夾**寫出 compose 用到的附檔**:Dockerfile、`.env.example` 與反向代理設定,只寫 compose 用得到的。
4. Delegate 執行 `uv run scripts/check_deploy.py --compose <compose.yaml 的路徑> --plan <plan.md 的路徑> --spec <spec.md 的路徑> --step <S 編號>` **取得部署檔的驗證結果**;若有不過 → 跳至 Phase 2 Step 2。
5. Think **逐條對照憲法的條文**;若有不過 → 跳至 Phase 2 Step 2。
6. Report **交出部署檔與待決問題**,附上憲法的對照結果:拿不準、要使用者決定的事不在中途詢問,一起列在這裡。

<details open>
<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>

```mermaid
flowchart TD
    subgraph P1["Phase 1: 盤點部署需求"]
        P1S1["1. Read：這次要分析的介面"]
        G_P1S1_1{"plan.md 指派了這一步？"}
        P1S2["2. Ask：這次要分析的<br/>端點、介面與需求出處"]
        P1S3["3. Read：分析的依據"]
        P1S4["4. Delegate：取得套<br/>用到部署檔的憲法條文"]
        P1S5["5. Think：盤點要跑的服務與對外入口"]
    end
    subgraph P2["Phase 2: 寫出部署檔"]
        P2S1["1. Think：定下每個服務的細節"]
        P2S2["2. Write：寫出 compose.yaml"]
        P2S3["3. Write：寫出 compose 用到的附檔"]
        P2S4["4. Delegate：取得部署檔的驗證結果"]
        G_P2S4_1{"有不過？"}
        P2S5["5. Think：逐條對照憲法的條文"]
        G_P2S5_1{"有不過？"}
        P2S6["6. Report：交出部署檔與待決問題"]
    end
    End["結束"]
    P1S1 --> G_P1S1_1
    G_P1S1_1 -->|是| P1S3
    G_P1S1_1 -->|否| P1S2
    P1S2 --> P1S3
    P1S3 --> P1S4
    P1S4 --> P1S5
    P1S5 --> P2S1
    P2S1 --> P2S2
    P2S2 --> P2S3
    P2S3 --> P2S4
    P2S4 --> G_P2S4_1
    G_P2S4_1 -->|是| P2S2
    G_P2S4_1 -->|否| P2S5
    P2S5 --> G_P2S5_1
    G_P2S5_1 -->|是| P2S2
    G_P2S5_1 -->|否| P2S6
    P2S6 --> End
```
</details>
