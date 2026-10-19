# Rule 1 [must] - 每張表都有 `created_at` 與 `updated_at`
- 每張 Table 都有 `created_at timestamptz [not null]` 與 `updated_at timestamptz [not null]`,即使需求沒有提到時間
- 純關聯表(只有兩個外鍵組成主鍵)也一樣
- 為什麼:這個專案的資料同步工作以 `updated_at` 撈增量;少一張表有這個欄位,那張表的變動就永遠同步不到報表庫

## good example
- 購物車明細只是關聯表,**仍然有兩個時間欄位**
```
Table cart_items {
  cart_id varchar(32) [not null]
  product_id varchar(32) [not null]
  quantity integer [not null, note: '1–99,對外回 invalid-quantity']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  indexes {
    (cart_id, product_id) [pk]
  }
  Note: '需求: FR-004、FR-005、FR-006'
}
```

## bad example
- 同一張表,因為需求沒提到時間就**沒有時間欄位**;同步工作撈不到購物車的變動
```
Table cart_items {
  cart_id varchar(32) [not null]
  product_id varchar(32) [not null]
  quantity integer [not null, note: '1–99,對外回 invalid-quantity']
  indexes {
    (cart_id, product_id) [pk]
  }
  Note: '需求: FR-004、FR-005、FR-006'
}
```
