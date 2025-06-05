from flask import Blueprint, request, abort
from extensions import line_bot_api, handler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

message_bp = Blueprint('message', __name__)

@message_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    print("=== Callback Body ===")
    print(body)
    print("=== Signature ===")
    print(signature)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("handle error:", e)
        import traceback; traceback.print_exc()
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="你說了：" + event.message.text)
    )
