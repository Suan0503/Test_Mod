import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main"))

from flask import Blueprint, request, abort
from extensions import handler
from linebot.exceptions import InvalidSignatureError
import traceback

message_bp = Blueprint('message', __name__)

@message_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("❗ callback 發生例外：", e)
        traceback.print_exc()
        abort(500)
    return "OK"

# ⭐ 讓 @handler.add(...) 生效
from handler import (
    follow,
    image,
    verify,
    report,
    lottery,
    admin,
    menu,
)
