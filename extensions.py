"""
extensions.py
- 提供全域的 SQLAlchemy 實例 (db)
- 初始化 LINE Bot SDK 的 LineBotApi 與 WebhookHandler
- 以正式環境為準：若環境變數缺少會直接 raise 錯誤（不做覆寫或 fallback）
- 關閉或降低預設的 debug/log 等級，避免大量除錯訊息出現
"""

import os
import logging
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from linebot import LineBotApi, WebhookHandler

# 載入 .env（如有）
load_dotenv()

# 將全域 logging 等級提高到 WARNING，避免 debug/info 訊息被輸出
# 若你想更細緻控制，可改用 logging.getLogger("your.logger").setLevel(...)
logging.basicConfig(level=logging.WARNING)
logging.getLogger().setLevel(logging.WARNING)

# SQLAlchemy 實例（在 app.py 中呼叫 db.init_app(app)）
db = SQLAlchemy()

# Flask-Migrate 實例 (在 app.py 中呼叫 migrate.init_app(app, db))
migrate = Migrate()

# 初始化 LINE Bot 客戶端（正式環境行為：必要環境變數缺少時直接失敗）
try:
    LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
except KeyError as e:
    # 直接 raise，讓部署或啟動階段能早期發現設定問題
    missing = e.args[0]
    raise RuntimeError(
        f"環境變數 {missing} 未設定。請在環境或 .env 檔中設定 LINE_CHANNEL_ACCESS_TOKEN 與 LINE_CHANNEL_SECRET。"
    )

# 不再進行任何覆寫；正式建立 SDK 實例
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
