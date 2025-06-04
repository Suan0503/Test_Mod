
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, FollowEvent, ImageMessage
from linebot.exceptions import InvalidSignatureError
from dotenv import load_dotenv
import os
import traceback

from routes.verify import handle_verification
from routes.admin import handle_manual_verification

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

message_bp = Blueprint("message_bp", __name__)

@message_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("❗ Webhook error:", e)
        traceback.print_exc()
        abort(500)
    return "OK"

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text="歡迎加入～請輸入手機號碼進行驗證（含09開頭）")
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    # 分派到不同邏輯模組
    if text.startswith("手動驗證") or user_id in text:
        handle_manual_verification(event, line_bot_api)
    else:
        handle_verification(event, line_bot_api)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # 若有需要驗證圖片截圖再擴充至 verify.py
    pass
