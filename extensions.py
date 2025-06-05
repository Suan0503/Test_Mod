from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
import os

db = SQLAlchemy()
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
