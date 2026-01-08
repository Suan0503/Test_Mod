# 🚀 Test_Mod 販售版快速開始指南

## 📋 目錄

1. [環境需求](#環境需求)
2. [快速部署](#快速部署)
3. [首次設定](#首次設定)
4. [基本使用](#基本使用)
5. [常見問題](#常見問題)

---

## 環境需求

### 必要條件
- Python 3.8+
- PostgreSQL 或 MySQL
- LINE Bot Channel（已建立）

### 依賴套件
```bash
Flask
Flask-SQLAlchemy
Flask-Migrate
line-bot-sdk
python-dotenv
APScheduler
pytz
```

---

## 快速部署

### Step 1: 複製專案
```bash
git clone <repository-url>
cd Test_Mod
```

### Step 2: 安裝依賴
```bash
pip install -r requirements.txt
```

### Step 3: 設定環境變數
建立 `.env` 檔案：
```env
# LINE Bot 設定
CHANNEL_ACCESS_TOKEN=your_channel_access_token
CHANNEL_SECRET=your_channel_secret

# 資料庫設定
DATABASE_URL=postgresql://user:password@localhost/dbname

# Flask 設定
SECRET_KEY=your_secret_key_here

# LINE Notify（選用）
LINE_NOTIFY_TOKEN=your_notify_token
```

### Step 4: 初始化資料庫
```bash
# 執行資料庫遷移
flask db upgrade

# 初始化指令配置
python -c "from utils.feature_control import init_command_config; init_command_config()"
```

### Step 5: 設定管理員
編輯 `storage.py`：
```python
ADMIN_IDS = {
    'U5ce6c382d12eaea28d98f2d48673b4b8',  # 替換成你的 LINE User ID
    # 可新增多個管理員
}
```

### Step 6: 啟動服務
```bash
# 開發環境
python app.py

# 正式環境（使用 gunicorn）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Step 7: 設定 Webhook
在 LINE Developers Console 設定 Webhook URL：
```
https://your-domain.com/callback
```

---

## 首次設定

### 1. 測試 Bot 連線
1. 用手機加入你的 LINE Bot 為好友
2. 傳送任意訊息測試回應
3. 確認 Bot 正常運作

### 2. 建立測試群組
1. 建立一個 LINE 群組
2. 邀請 Bot 加入群組
3. 在群組中傳送「驗證資訊」測試

### 3. 設定功能方案
在群組中執行（需要管理員權限）：
```
/功能設定
```
查看當前狀態（預設全功能開啟）

設定適合的方案：
```
/設定方案 basic
```

### 4. 生成 TOKEN
```
/生成token
```
記錄生成的 TOKEN，用於後續 API 驗證

---

## 基本使用

### 管理員指令

#### 查看功能狀態
```
/功能設定
```
顯示當前群組的功能配置、TOKEN 和到期資訊

#### 切換功能開關
```
/設定功能 draw
```
開啟或關閉「每日抽獎」功能

#### 套用功能方案
```
/設定方案 standard
```
套用標準版方案（驗證、回報文、抽獎券、每日抽獎、儲值錢包）

#### 重新生成 TOKEN
```
/生成token
```
為群組生成新的專屬 TOKEN

### 使用者指令

#### 查看驗證資訊
```
驗證資訊
```
顯示個人驗證狀態和資料

#### 提交回報文
```
回報文
```
進入回報文提交流程

#### 每日抽獎
```
每日抽獎
```
參加每日抽獎活動

#### 查看抽獎券
```
折價券管理
```
查看今日抽獎券和本月回報文券

#### 查看錢包
```
我的錢包
```
（需在 Web 管理面板設定）

---

## 功能方案說明

### 🔹 基礎版 (basic)
**價格**: 建議 NT$ 1,000/月  
**功能**: 
- ✅ 驗證功能
- ✅ 回報文功能
- ✅ 抽獎券功能

**適合**: 小型店家、試用客戶

---

### 🔸 標準版 (standard)
**價格**: 建議 NT$ 2,500/月  
**功能**: 
- ✅ 基礎版所有功能
- ✅ 每日抽獎
- ✅ 儲值錢包

**適合**: 一般商家、餐飲業

---

### 🔶 專業版 (professional)
**價格**: 建議 NT$ 5,000/月  
**功能**: 
- ✅ 標準版所有功能
- ✅ 管理面板
- ✅ 預約系統

**適合**: 美容業、預約制服務業

---

### ⭐ 企業版 (enterprise)
**價格**: 建議 NT$ 10,000/月  
**功能**: 
- ✅ 專業版所有功能
- ✅ 薪資管理
- ✅ 手動驗證
- ✅ 圖文選單
- ✅ 統計功能
- ✅ 廣告專區

**適合**: 大型商家、完整需求客戶

---

## 常見問題

### Q1: 如何找到我的 LINE User ID？
**A**: 
1. 在 LINE Bot 中傳送訊息
2. 查看伺服器日誌，會顯示 `user_id=Uxxxxx...`
3. 或使用 LINE Developers Console 的測試工具

### Q2: 功能設定指令沒有反應？
**A**: 
1. 確認你的 User ID 在 `ADMIN_IDS` 中
2. 確認在群組中使用（非私訊）
3. 檢查指令格式是否正確

### Q3: 資料庫連線失敗？
**A**: 
1. 檢查 `DATABASE_URL` 格式是否正確
2. 確認資料庫服務正在運行
3. 檢查防火牆設定
4. PostgreSQL URL 需使用 `postgresql://` 開頭（非 `postgres://`）

### Q4: Webhook 驗證失敗？
**A**: 
1. 確認 `CHANNEL_SECRET` 設定正確
2. 檢查 HTTPS 憑證是否有效
3. 確認伺服器可從外部存取
4. 查看 LINE Developers Console 的錯誤訊息

### Q5: 如何新增更多管理員？
**A**: 
編輯 `storage.py`，在 `ADMIN_IDS` 中新增 User ID：
```python
ADMIN_IDS = {
    'U5ce6c382...',  # 管理員 1
    'U2bcd6300...',  # 管理員 2
    'Uxxxxx...',     # 管理員 3
}
```

### Q6: 功能使用記錄在哪裡查看？
**A**: 
查詢 `feature_usage_log` 資料表：
```sql
SELECT * FROM feature_usage_log 
ORDER BY created_at DESC 
LIMIT 100;
```

### Q7: 如何備份群組設定？
**A**: 
使用提供的匯出功能：
```python
from utils.feature_control import export_group_settings
export_group_settings("backup.json")
```

### Q8: 可以設定功能到期日嗎？
**A**: 
可以，程式碼範例：
```python
from datetime import datetime, timedelta
from utils.feature_control import create_group_features

expires_at = datetime.utcnow() + timedelta(days=30)
create_group_features(group_id, features, expires_at=expires_at)
```

### Q9: 如何客製化方案？
**A**: 
1. 先套用最接近的方案
2. 再用 `/設定功能` 調整個別功能
3. 或直接編輯 `FEATURE_CATEGORIES` 新增自訂方案

### Q10: 系統效能如何優化？
**A**: 
1. 定期清理 `feature_usage_log` 舊資料
2. 確認資料庫索引正常
3. 使用 Redis 快取常用查詢
4. 啟用資料庫連接池

---

## 📞 取得協助

### 文件資源
- 📖 [功能控制指南](FEATURE_CONTROL_GUIDE.md)
- 📋 [部署檢查清單](DEPLOYMENT_CHECKLIST.md)
- 💡 [配置範例](CONFIGURATION_EXAMPLES.md)
- 📝 [更新日誌](CHANGELOG.md)

### 技術支援
- 📧 Email: support@example.com
- 💬 LINE: @example
- 🌐 文件: https://docs.example.com

### 社群資源
- 💻 GitHub: https://github.com/example/test-mod
- 💬 Discord: https://discord.gg/example
- 📱 Facebook: https://fb.com/example

---

## 🎯 下一步

完成基本設定後，建議：

1. ✅ 閱讀 [功能控制指南](FEATURE_CONTROL_GUIDE.md) 了解進階功能
2. ✅ 參考 [配置範例](CONFIGURATION_EXAMPLES.md) 學習不同場景配置
3. ✅ 使用 [部署檢查清單](DEPLOYMENT_CHECKLIST.md) 確保部署完整
4. ✅ 設定監控和備份機制
5. ✅ 準備客戶培訓資料

---

**祝您使用愉快！🎉**

如有任何問題，歡迎隨時聯繫技術支援團隊。
