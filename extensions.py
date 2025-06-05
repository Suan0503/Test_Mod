from linebot import LineBotApi, WebhookHandler
from flask_sqlalchemy import SQLAlchemy
import redis
import os

# LINE Bot
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# SQLAlchemy
db = SQLAlchemy()

# Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
    password=os.getenv("REDIS_PASSWORD", None)
)
