# 提案:以產出物為中心的模組化憲法(最小版)

> 狀態:**提案範例(未實作、未驗證)**。本資料夾只示範檔案長什麼樣子;
> 文中提到的 `constitution` skill 還不存在。

## 澄清結果(2026-10-19)

| 題號 | 問題 | 回答 |
|---|---|---|
| Q1 | 憲法可以翻掉 Skill 內建的規範嗎? | 可以取代,但要點名是哪一條;主要是限制產出物 |
| Q2 | 憲法的檔案依什麼切開? | 依 Skill 分資料夾,資料夾內依產出物分檔 |
| Q3 | 憲法條文怎麼被檢查? | 條文可以附機器斷言,有就跑,沒有就由 AI 對照 |
| Q4 | 要不要分全域與專案兩層? | 只有專案層,從範本初始化 |
| Q5 | 跨多種產出物的約束放哪裡? | 放 `_shared/`,檔頭宣告 `applies_to` |

最小版先不做 Q1 的「取代」與 Q3 的「機器斷言」,但兩者都留了接口,見〈之後再加的〉。

## 和 Spec-Kit 的差別

| | Spec-Kit | 本提案 |
|---|---|---|
| 約束對象 | 原則(程式碼品質、效能…) | 一個產出物,例如 `api-plan/openapi` |
| 檔案 | 一個 `constitution.md` | 每個產出物一個檔,加上 `_shared/` |
| 什麼時候檢查 | `plan` 填一張 Constitution Check 表 | 每支 Skill 寫完自己的產出物就逐條對照 |
| 和 Skill 規範的關係 | 憲法優先,但看不出翻掉了哪條 | 只能加嚴;Skill 規範照樣成立 |
| 版本 | semver 加 Sync Impact Report | 用 git 歷史 |

## 檔案結構

```
<專案>/constitution/
├── _shared/時間格式.md          ← 跨產出物:檔頭 applies_to 宣告管誰
├── api-plan/openapi.md
├── data-plan/schema.md
└── specify/spec.md
```

- **路徑就是約束對象**:`<skill>/<產出物>.md`
- **合法的路徑從 Skill 推得出來,不另外維護清單**:`<skill>` 是 SDD 流程的 Skill 名稱,
  `<產出物>` 是那支 Skill `templates/` 底下的檔名去掉 `.template` 與副檔名,不含 `.example` 檔與交給 sub agent 的指示

  | Skill | 合法的產出物 |
  |---|---|
  | specify | `spec` |
  | technical-research | `research`、`techstack` |
  | system-analysis | `plan` |
  | api-plan | `openapi`、`asyncapi` |
  | data-plan | `schema` |
  | deploy-plan | `compose` |
  | uiux-plan | `style`、`mock`、`page`、`states` |
  | tasks | `tasks` |

- **沒有檔的產出物就照 Skill 預設**,不需要建空檔
- **約束跟著產出物走**:`clarify-over-specs` 會改寫 spec.md,所以也要遵守 `specify/spec.md`

## 條文格式

照 RuleFile 格式:`# Rule N [must|should] - 標題`、條列、`為什麼`、good/bad example。
`_shared/` 底下的檔另外在檔頭寫 `applies_to: [<skill>/<產出物>, ...]`。

條文只能**加嚴**:Skill 自己的規範照樣成立,憲法再往上疊。
兩者衝突時以 Skill 為準,並在報告裡列出衝突,讓人決定要改憲法還是改 Skill。

## Skill 怎麼接上(流程不變,加兩步)

以 api-plan 為例:

| 位置 | 加什麼 |
|---|---|
| Phase 1 Step 3 Read 依據 | 多讀 `constitution/api-plan/openapi.md`,以及 `_shared/` 裡 `applies_to` 含 `api-plan/openapi` 的檔 |
| Phase 2 Step 4 檢查之後 | Think 逐條對照讀到的條文;不過就跳回寫檔的那一步;報告每條結果並標明「AI 判定」 |

專案沒有 `constitution/` 時,這兩步什麼都不做。

## `constitution` skill(新增)

- **init**:把範本複製進 `<專案>/constitution/`
- **amend**:新增或修改條文;缺口轉交 `clarify`;寫完確認路徑合法、`applies_to` 合法、每條都有 good/bad example

## 憲法不放什麼

- 流程:步驟、順序、要不要問使用者(Skill 的事)
- 測試策略與覆蓋率(之後另開 `test-plan`、`test-tdd`)
- 團隊流程:PR 審查、合併關卡

## 之後再加的(真的碰到再做)

| 什麼時候 | 加什麼 | 接口 |
|---|---|---|
| 某條條文 AI 常判錯 | 替那條補機器斷言:YAML 產出物(OpenAPI、AsyncAPI、compose)用 Spectral ruleset;DBML 要先轉 JSON(未驗證) | 條文多一段 `## 斷言`,good example 要通過、bad example 要不過 |
| 第一次真的要翻掉 Skill 的預設 | 在那支 Skill 的規範加一個具名的**可覆寫點**與預設值,憲法只填那個點 | 條文多一段 `## 可覆寫點`;只有讀那個點的檢查要分支 |

2026-10-19 已實測 Spectral(`@stoplight/spectral-cli@6.15.0`)對 OpenAPI 與 compose.yaml 的 good/bad 檔一綠一紅。

## 落地順序

1. `constitution` skill:init 與 amend
2. 拿 api-plan 試點:加兩步,用本範例的 `api-plan/openapi.md` 實跑
3. 推到其他 Skill
