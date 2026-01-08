# 🎯 Test_Mod - 販售版 LINE Bot 系統

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**功能模組化 | 資料庫儲存 | 中文化指令 | 多方案管理**

</div>

---

## 📋 專案簡介

Test_Mod 是一個專為商業販售設計的 LINE Bot 系統，提供完整的功能拆分與授權管理機制。參考 FanFan 專案架構，採用資料庫儲存模式，支援多種功能方案，適合對外提供 SaaS 服務。

### ✨ 核心特色

- 🎯 **功能模組化** - 12 種可獨立控制的功能模組
- 💾 **資料庫儲存** - 所有設定永久保存於資料庫
- 🔐 **TOKEN 驗證** - 每個群組獨立 TOKEN，支援 API 驗證
- 📦 **多方案管理** - 預設 4 種方案，可快速部署
- 🇹🇼 **完整中文化** - 所有指令與介面全中文
- 📊 **使用統計** - 自動記錄功能使用情況

---

## 🚀 快速開始

### 安裝步驟

```bash
# 1. 複製專案
git clone <repository-url>
cd Test_Mod

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定環境變數（建立 .env 檔案）
cp .env.example .env
# 編輯 .env 填入您的設定

# 4. 初始化資料庫
flask db upgrade

# 5. 初始化指令配置
python -c "from utils.feature_control import init_command_config; init_command_config()"

# 6. 啟動服務
python app.py
```

詳細步驟請參考 [快速開始指南](QUICK_START.md)

---

## 🎨 功能列表

### 核心功能模組

| 模組 | 功能 | 適用方案 |
|------|------|----------|
| 🔐 驗證功能 | LINE 用戶身份驗證 | 全方案 |
| 📝 回報文 | 回報文提交與管理 | 全方案 |
| 🎟️ 抽獎券 | 抽獎券查詢與管理 | 全方案 |
| 🎰 每日抽獎 | 每日抽獎活動 | 標準版+ |
| 💰 儲值錢包 | 儲值金管理系統 | 標準版+ |
| 🎛️ 管理面板 | Web 管理後台 | 專業版+ |
| 📅 預約系統 | 預約排程功能 | 專業版+ |
| 💵 薪資管理 | 薪資計算與查詢 | 企業版 |
| ✋ 手動驗證 | 人工審核機制 | 企業版 |
| 🎨 圖文選單 | LINE 圖文選單 | 企業版 |
| 📊 統計功能 | 數據統計報表 | 企業版 |
| 📢 廣告專區 | 廣告展示系統 | 企業版 |

---

## 📦 方案說明

### 🔹 基礎版 (Basic)
**建議售價**: NT$ 1,000/月

```
✅ 驗證功能
✅ 回報文功能
✅ 抽獎券功能
```

**適合**: 小型店家、試用客戶

---

### 🔸 標準版 (Standard)
**建議售價**: NT$ 2,500/月

```
✅ 基礎版所有功能
✅ 每日抽獎
✅ 儲值錢包
```

**適合**: 一般商家、餐飲業

---

### 🔶 專業版 (Professional)
**建議售價**: NT$ 5,000/月

```
✅ 標準版所有功能
✅ 管理面板
✅ 預約系統
```

**適合**: 美容業、預約制服務

---

### ⭐ 企業版 (Enterprise)
**建議售價**: NT$ 10,000/月

```
✅ 專業版所有功能
✅ 薪資管理
✅ 手動驗證
✅ 圖文選單
✅ 統計功能
✅ 廣告專區
```

**適合**: 大型商家、完整需求

---

## 🎯 管理指令

### 群組管理員指令

```bash
# 查看功能狀態
/功能設定

# 切換功能開關
/設定功能 draw

# 套用功能方案
/設定方案 standard

# 生成 TOKEN
/生成token
```

### 使用者指令

```bash
驗證資訊     # 查詢驗證狀態
回報文       # 提交回報文
每日抽獎     # 參加抽獎
折價券管理   # 查看券記錄
我的錢包     # 查詢錢包
廣告專區     # 瀏覽廣告
```

完整指令說明請參考 [功能控制指南](FEATURE_CONTROL_GUIDE.md)

---

## 🏗️ 系統架構

```
Test_Mod/
├── app.py                          # Flask 應用主程式
├── models.py                       # 資料庫模型
├── extensions.py                   # Flask 擴充初始化
├── config.py                       # 配置檔
├── storage.py                      # 儲存設定（ADMIN_IDS）
│
├── hander/                         # 事件處理器
│   ├── entrypoint.py              # 主要訊息處理入口
│   ├── admin_feature.py           # 功能控制指令處理
│   ├── admin.py                   # 管理員指令
│   ├── verify.py                  # 驗證處理
│   ├── report.py                  # 回報文處理
│   └── ...
│
├── routes/                         # Web 路由
│   ├── admin.py                   # 管理後台路由
│   ├── message.py                 # 訊息 Webhook
│   └── ...
│
├── utils/                          # 工具模組
│   ├── feature_control.py         # 功能控制核心 ⭐
│   ├── menu_helpers.py            # 選單輔助
│   ├── db_utils.py                # 資料庫工具
│   └── ...
│
├── migrations/                     # 資料庫遷移
│   └── versions/
│       └── 0004_feature_control.py # 功能控制表 ⭐
│
├── templates/                      # HTML 模板
├── static/                         # 靜態資源
│
└── docs/                          # 文件
    ├── FEATURE_CONTROL_GUIDE.md   # 功能控制指南 ⭐
    ├── QUICK_START.md             # 快速開始 ⭐
    ├── DEPLOYMENT_CHECKLIST.md    # 部署清單 ⭐
    ├── CONFIGURATION_EXAMPLES.md  # 配置範例 ⭐
    └── CHANGELOG.md               # 更新日誌 ⭐
```

---

## 💾 資料庫架構

### 功能控制相關表

#### GroupFeatureSetting
```sql
群組功能設定表
- group_id: 群組 ID
- token: 專屬 TOKEN
- features: 功能列表（JSON）
- expires_at: 授權到期日
- is_active: 是否啟用
```

#### CommandConfig
```sql
指令配置表
- command_key: 功能鍵值
- command_zh: 中文指令
- feature_category: 功能分類
- is_admin_only: 是否管理員專用
```

#### FeatureUsageLog
```sql
使用記錄表
- group_id: 群組 ID
- user_id: 用戶 ID
- feature_key: 使用功能
- created_at: 使用時間
```

完整架構請參考 [資料庫文件](docs/database.md)

---

## 📚 文件導覽

- 📖 [功能控制指南](FEATURE_CONTROL_GUIDE.md) - 完整功能說明
- 🚀 [快速開始指南](QUICK_START.md) - 部署與設定
- ✅ [部署檢查清單](DEPLOYMENT_CHECKLIST.md) - 上線前確認
- 💡 [配置範例集](CONFIGURATION_EXAMPLES.md) - 實用範例
- 📝 [更新日誌](CHANGELOG.md) - 版本歷程

---

## 🔧 技術棧

- **後端框架**: Flask 2.x
- **資料庫**: PostgreSQL / MySQL
- **LINE SDK**: line-bot-sdk
- **排程系統**: APScheduler
- **遷移工具**: Flask-Migrate
- **ORM**: SQLAlchemy

---

## 🌟 更新亮點 (v2.0)

✅ 完整功能拆分系統  
✅ 資料庫儲存模式  
✅ 指令全面中文化  
✅ TOKEN 驗證機制  
✅ 多方案快速部署  
✅ 使用統計記錄  
✅ 完整文件支援  

詳細更新請見 [CHANGELOG.md](CHANGELOG.md)

---

## 📊 使用統計

系統自動記錄：
- 功能使用頻率
- 用戶活躍度
- 群組使用狀況
- 熱門功能分析

可用於優化服務和制定方案策略

---

## 🔐 安全性

- ✅ TOKEN 機制保護 API
- ✅ 管理員權限控制
- ✅ SQL Injection 防護
- ✅ 敏感資料加密
- ✅ HTTPS 強制使用

---

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

## 📞 技術支援

### 聯絡方式
- 📧 Email: support@example.com
- 💬 LINE: @example
- 📱 Phone: 0912-345-678

### 社群資源
- 💻 GitHub: [專案首頁](https://github.com/example/test-mod)
- 📖 文件: [線上文件](https://docs.example.com)
- 💬 Discord: [加入社群](https://discord.gg/example)

---

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

---

## 🙏 致謝

- 參考 [FanFan](https://github.com/example/fanfan) 專案的功能控制架構
- LINE Messaging API 官方文件
- Flask 與 SQLAlchemy 社群

---

## 📈 發展路線

### v2.1 (計畫中)
- [ ] 授權自動續約提醒
- [ ] 功能使用配額限制
- [ ] 統計儀表板

### v3.0 (長期目標)
- [ ] 完整 SaaS 管理平台
- [ ] 線上自助開通
- [ ] AI 智能客服整合

---

<div align="center">

**⭐ 如果這個專案對您有幫助，請給我們一個星星！⭐**

Made with ❤️ by Test_Mod Team

</div>
