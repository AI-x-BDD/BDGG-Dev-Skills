# Rule 1 [must] - 錯誤一律帶 traceId
- AsyncAPI 推送給呼叫者的錯誤訊息 payload,把 `traceId` 列為必填欄位
- `traceId` 是伺服器為這則訊息產生的追蹤編號,與伺服器日誌裡同一筆紀錄的編號相同
- 為什麼:這個專案靠玩家回報的錯誤畫面截圖排查問題;錯誤裡沒有 traceId,就對不到伺服器那一筆日誌

## good example
- 錯誤訊息**把 `traceId` 列為必填**
```yaml
Error:
  type: object
  required: [type, code, message, traceId]
  properties:
    traceId: { type: string, description: 伺服器日誌裡同一筆紀錄的追蹤編號 }
```

## bad example
- 同一則錯誤訊息,但**沒有 `traceId`**;玩家回報的截圖對不到任何一筆日誌
```yaml
Error:
  type: object
  required: [type, code, message]
```
