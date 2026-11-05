# 真實環境驗收規劃:訂閱頻道

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-29

## 驗收項目

| V | 對象 | 真實元件 | 自動測試的替身 | 實跑做法 | 樣本 | 通過條件 | 副作用與護欄 | 判定者 |
|---|---|---|---|---|---|---|---|---|
| V1 | SC-001 | yt-dlp | tests/fixtures/fake_ytdlp | 真的 yt-dlp 讀一個公開頻道 | 公開頻道,未調過規則 | 列出至少 1 支新片 | 只寫暫存 volume;只讀公開頁面 | 腳本 |
| V2 | SC-002、故事 1 | 瀏覽器、htmx | tests 的 htmx 替身 | Playwright 按訂閱並等工作完成 | 不適用 | 工作頁顯示完成,筆記列表多一筆 | 用 docker run --rm 與暫存 volume,不用 compose up | 腳本 |

## 要使用者同意的項目

- 無
