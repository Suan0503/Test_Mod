from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
import os

db = SQLAlchemy()

# LINE Bot 設定（正式環境）
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", ""))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET", ""))
