from flask import Blueprint, request, abort
from app import handler, line_bot_api
from linebot.models import MessageEvent, TextMessage, TextSendMessage

message_bp = Blueprint('message', __name__)

@message_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception:
        abort(400)
    return "OK"

# LINE Bot 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="收到訊息：" + event.message.text)
    )
