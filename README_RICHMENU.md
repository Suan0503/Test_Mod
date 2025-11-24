# Rich Menu 互動改版（初版）

本專案已導入 LINE Rich Menu 狀態切換：

## 狀態對應
- DEFAULT：新加入 / 未驗證，用於引導驗證。
- VERIFIED：已驗證用戶，一般功能（抽獎、券紀錄、活動快訊等）。
- ADMIN：管理員功能（手動驗證、廣告專區）。

## 啟動流程
啟動 `app.py` 會執行 `ensure_rich_menus()`：
1. 讀取現有 RichMenu 列表。
2. 無對應名稱（`RM_DEFAULT`, `RM_VERIFIED`, `RM_ADMIN`）則自動建立。
3. 只建立結構，不自動上傳背景圖片（可後續於 LINE Console 替換）。

## 切換邏輯
- FollowEvent：綁定 DEFAULT。
- 驗證成功（或查看已驗證資訊）：切到 VERIFIED。
- 管理員在驗證處理流程/指令操作時：切到 ADMIN。
- 後台管理員可使用 `/admin/richmenu/switch` 手動切換。

## 後台 API
POST `/admin/richmenu/switch`
Form 參數：
- line_user_id：目標使用者 LINE User ID
- state：DEFAULT / VERIFIED / ADMIN
- admin_id（可選）：操作者 ID，若提供會驗證是否在 ADMIN_IDS

## 工具模組
`utils/richmenu.py`：
- `ensure_rich_menus()`：建立或取得三種狀態的 RichMenu ID。
- `switch_rich_menu(line_user_id, state)`：綁定指定使用者。
- `RICHMENU_STATES`：可用狀態清單。

## 資料表
`RichMenuBinding`：記錄使用者目前狀態與綁定的 rich_menu_id，方便後續分析或手動對照。

## 後續可優化
1. 背景圖片自動上傳與設定（`upload_rich_menu_image`）。
2. 增加更多狀態（如 EVENT、SUSPENDED）。
3. 將文字指令改為統一 Postback 行為（目前仍保留原文字回覆）。
4. 增加報表：各狀態下的使用者分佈與切換時間記錄。

## 注意
- 初次啟動需確保 LINE Channel Access Token 有建立 RichMenu 權限。
- 若建立失敗 `_richmenu_cache` 會是空 dict，不影響其他功能，但不會執行綁定。

## 回滾
若要回到純文字模式：
1. 停用 `utils.richmenu` 匯入與 `switch_rich_menu` 呼叫。
2. 刪除資料表 `rich_menu_binding`（可留存備查）。

---
此文件為初版示意，可再根據實際 UI 設計調整區塊與行為。
