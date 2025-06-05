from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
import redis
import os

db = SQLAlchemy()
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
    password=os.getenv("REDIS_PASSWORD", None)
)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
