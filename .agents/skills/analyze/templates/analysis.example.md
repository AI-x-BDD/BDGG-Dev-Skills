# 跨產出物分析: 線上商店

**Feature**: [spec.md](./spec.md) | **Tasks**: [tasks.md](./tasks.md) | **Constitution**: `constitution/`

## 判定

**最新一輪:第 2 輪(2026-10-30)— ✅ 可以進 `/implement`**

沒有未解決的 CRITICAL 或 HIGH;剩 1 個 MEDIUM(A6),不擋實作,建議實作前順手修掉。

## 檢查範圍

| 產出物 | 產出的步驟 |
|---|---|
| `spec.md` | `/specify` |
| `research.md`、`techstack.md` | `/technical-research` |
| `plan.md` | `/system-analysis` |
| `contracts/shop.openapi.yaml`、`contracts/shop.asyncapi.yaml` | `/api-plan` |
| `contracts/shop.dbml` | `/data-plan` |
| `prototype/` | `/ui-plan` |
| `tasks.md` | `/tasks` |
| `constitution/api-plan/error.md` | `/constitution` |

---

## 第 1 輪(2026-10-29)

### 前置檢查

| 腳本 | 結果 |
|---|---|
| `specify/scripts/check_spec.py` | ✅ 通過 |
| `system-analysis/scripts/check_plan.py` | ✅ 通過 |
| `tasks/scripts/check_tasks.py` | ✅ 通過(錨點存在、介面元素全覆蓋) |

### 問題

| ID | 類別 | 嚴重度 | 位置 | 摘要 | 回哪一步 |
|---|---|---|---|---|---|
| A1 | 憲法 | CRITICAL | `constitution/api-plan/error.md` 〈錯誤回應一律帶 traceId〉;`contracts/shop.openapi.yaml` § `components.schemas.Error` | 憲法 MUST 條文要求每個錯誤回應帶 `traceId`,`Error` 的 `required` 只有 `code`、`message` | `/api-plan` |
| A2 | 矛盾 | HIGH | `spec.md` § FR-007;`contracts/shop.dbml` § `Table orders`;`contracts/shop.openapi.yaml` § `checkout` | FR-007 寫「下單後 30 分鐘內未付款自動取消」,`orders.payment_expires_at` 的 note 與 `checkout` 的說明都寫 15 分鐘 | `/data-plan`、`/api-plan` |
| A3 | 遺漏 | HIGH | `spec.md` § 使用者故事 3 驗收情境 2;`plan.md` § 端點盤點 | 驗收情境要「逾時取消的訂單在『我的訂單』顯示已取消」,但 E1、E2 的需求出處都沒列使用者故事 3,所以 OpenAPI 沒有查訂單列表的 operation、原型沒有訂單頁 | `/system-analysis` |
| A4 | 無法實作 | HIGH | `research.md` § R3;`tasks.md` | R3 決定「逾時取消以每分鐘排程掃描 `pending` 訂單」,`tasks.md` 沒有任何任務做排程;照現在的任務做完,FR-007 的自動取消不會發生 | `/tasks` |
| A5 | 無法追溯 | MEDIUM | `tasks.md` § T031;`spec.md` § FR-005 | T031「實作優惠券折抵」以 📎 引用 FR-005,但 FR-005 只講「結帳金額 = 商品小計 + 運費」;優惠券不在任何需求與規格檔裡 | `/tasks` |

### 追溯缺口

只列有缺口的需求;其餘需求從規格檔到任務都接得上。

| 需求 | 規格檔元素 | 任務 | 缺口 |
|---|---|---|---|
| FR-007 自動取消 | `shop.dbml` § `Table orders`(期限值錯) | 無 | A2、A4 |
| 使用者故事 3 驗收情境 2 | 無 | 無 | A3 |

### 轉交 `/clarify-over-specs`

單份文件內的模糊不屬於本步驟,標記後轉交:

| 位置 | 為什麼要澄清 |
|---|---|
| `spec.md` § NFR-002 | 「結帳頁要快速載入」沒有可量測的門檻,下游沒辦法據以設計與驗收 |

### 修正順序

1. `/system-analysis` 把使用者故事 3 補進 E1、E2 的需求出處(A3),再依序重跑 `/api-plan`、`/ui-plan`
2. `/api-plan` 補 `traceId`(A1)、期限改 30 分鐘(A2);`/data-plan` 期限改 30 分鐘(A2)
3. `/clarify-over-specs` 澄清 NFR-002
4. `/tasks` 補排程任務(A4)、刪 T031(A5),並涵蓋第 1 步新增的介面元素
5. 重跑 `/analyze`

---

## 第 2 輪(2026-10-30)

### 前置檢查

| 腳本 | 結果 |
|---|---|
| `specify/scripts/check_spec.py` | ✅ 通過 |
| `system-analysis/scripts/check_plan.py` | ✅ 通過 |
| `tasks/scripts/check_tasks.py` | ✅ 通過 |

### 上一輪的問題

| ID | 狀態 | 依據 |
|---|---|---|
| A1 | ✅ 已修正 | `shop.openapi.yaml` § `components.schemas.Error` 的 `required` 加上 `traceId` |
| A2 | ✅ 已修正 | `shop.dbml` § `Table orders` 與 `shop.openapi.yaml` § `checkout` 都改成 30 分鐘,與 FR-007 一致 |
| A3 | ✅ 已修正 | `plan.md` § 端點盤點的 E1、E2 列入使用者故事 3;新增 `shop.openapi.yaml` § `listOrders` 與 `prototype/orders.html` |
| A4 | ✅ 已修正 | `tasks.md` § T044 實作逾時取消排程,📎 `research.md` § R3 |
| A5 | ✅ 已修正 | `tasks.md` 已刪除 T031 |
| NFR-002 | ✅ 已澄清 | `/clarify-over-specs` 回寫為「結帳頁 LCP ≤ 2.5 秒(4G 網路)」 |

### 新問題

| ID | 類別 | 嚴重度 | 位置 | 摘要 | 回哪一步 |
|---|---|---|---|---|---|
| A6 | 矛盾 | MEDIUM | `spec.md` § 使用者故事 3 驗收情境 2;`prototype/orders.html` § `[data-state="cancelled"]` | 修 A3 時新增的訂單頁把取消的訂單標成「已失效」,需求寫的是「已取消」 | `/ui-plan` |
