from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
import config
from handlers.welcome import register_welcome_handler
from handlers.verify import register_verify_handlers
from handlers.menu import register_menu_handler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.verify_user import Base

app = Flask(__name__)
line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

# MySQL 資料庫連線設定
# 請將 user, password, host, port, dbname 改成你的 MySQL 資料庫資訊
DATABASE_URL = 'mysql+pymysql://user:password@host:3306/dbname'
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

# 註冊各種 handler

register_welcome_handler(handler)
register_verify_handlers(handler)
register_menu_handler(handler)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
