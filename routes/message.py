from flask import Blueprint, request, abort
from extensions import handler as webhook_handler
from linebot.exceptions import InvalidSignatureError
import traceback

message_bp = Blueprint('message', __name__)

# ⭐ 匯入 entrypoint（註冊所有事件處理器）
import handler.entrypoint  # noqa: F401

@message_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        webhook_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("❗ callback 發生例外：", e)
        traceback.print_exc()
        abort(500)
    return "OK"
