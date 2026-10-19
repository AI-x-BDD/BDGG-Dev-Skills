# Rule 1 [must] - 成功回應一律包成 `{data, meta}`
- 每個 2xx 的 `application/json` 回應,schema 的最外層是 `data` 與 `meta` 兩個必填欄位;`meta` 至少有必填的 `requestId`
- 列表回應的分頁資訊放在 `meta`(`total`、`page`),不放進 `data`
- 為什麼:前端共用一個 fetch 包裝,只認這個形狀;`requestId` 讓客服回報的問題能直接對到伺服器日誌

## good example
- 商品列表的 `data` 只放商品,**總數放在 `meta`**,`meta.requestId` 必填
```yaml
'200':
  description: 這一頁的商品摘要
  x-recipients: 呼叫者
  content:
    application/json:
      schema:
        type: object
        required: [data, meta]
        properties:
          data:
            type: array
            items: { $ref: '#/components/schemas/ProductSummary' }
          meta:
            type: object
            required: [requestId, total, page]
            properties:
              requestId: { type: string }
              total: { type: integer, minimum: 0 }
              page: { type: integer, minimum: 1 }
```

## bad example
- 同一個回應,但**直接回 `{items, total}`**;前端的 fetch 包裝拿不到 `data`,也沒有 `requestId`
```yaml
'200':
  description: 這一頁的商品摘要與總數
  x-recipients: 呼叫者
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ProductPage'
```

# Rule 2 [must] - 錯誤回應帶 `requestId`
- `Error` schema 除了 Skill 規定的 `code` 與 `message`,還有必填的 `requestId`
- 為什麼:使用者回報錯誤時通常只截得到錯誤畫面;錯誤回應帶著 `requestId`,客服才能從截圖對到伺服器日誌
- 本條是加嚴:`api-plan/rules/契約-規範.md` 要求的 `x-error-codes` 與 `code` enum 照樣要寫

## good example
- `Error` 在 Skill 要求的欄位之外**多了必填的 `requestId`**
```yaml
Error:
  type: object
  required: [code, message, requestId]
  properties:
    code:
      type: string
      enum: [INVALID_PAGE, INVALID_QUANTITY, PRODUCT_NOT_FOUND]
    message:
      type: string
    requestId:
      type: string
```

## bad example
- 同一個 schema,**照 Skill 預設只有 `code` 與 `message`**;錯誤畫面的截圖對不到任何一筆日誌
```yaml
Error:
  type: object
  required: [code, message]
  properties:
    code:
      type: string
      enum: [INVALID_PAGE, INVALID_QUANTITY, PRODUCT_NOT_FOUND]
    message:
      type: string
```
