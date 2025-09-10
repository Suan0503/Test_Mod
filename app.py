from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
import pytesseract
from PIL import Image
import io
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# LINE BOT 設定
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_CHANNEL_ACCESS_TOKEN')
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# PostgreSQL 設定
POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgresql://user:password@localhost:5432/yourdb')
engine = create_engine(POSTGRES_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 資料表範例
class OCRRecord(Base):
    __tablename__ = 'ocr_records'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    text = Column(String)

Base.metadata.create_all(bind=engine)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    # 基本回覆
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"你說的是：{event.message.text}")
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # 取得圖片內容
    message_content = line_bot_api.get_message_content(event.message.id)
    image = Image.open(io.BytesIO(message_content.content))
    # OCR 辨識
    ocr_text = pytesseract.image_to_string(image, lang='chi_tra+eng')
    # 儲存到資料庫
    session = SessionLocal()
    record = OCRRecord(user_id=event.source.user_id, text=ocr_text)
    session.add(record)
    session.commit()
    session.close()
    # 回覆辨識結果
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"OCR結果：{ocr_text}")
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
