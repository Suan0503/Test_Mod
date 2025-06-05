from flask import Blueprint, request, abort
from extensions import line_bot_api, handler, db
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
from models import Coupon
from utils.draw_utils import draw_coupon, has_drawn_today, save_coupon_record, get_today_coupon_flex
from utils.image_verification import extract_lineid_phone

message_bp = Blueprint('message', __name__)

@message_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("handle error:", e)
        import traceback; traceback.print_exc()
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    display_name = "用戶"

    if user_text in ["抽獎", "daily", "抽獎！", "我要抽獎"]:
        record = has_drawn_today(user_id, Coupon)
        if record:
            amount = record.amount
        else:
            amount = draw_coupon()
            save_coupon_record(user_id, amount, Coupon, db)
        flex_msg = get_today_coupon_flex(user_id, display_name, amount)
        line_bot_api.reply_message(event.reply_token, flex_msg)
        return

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="你說了：" + user_text)
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    temp_path = f"/tmp/{message_id}.jpg"
    with open(temp_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    phone, lineid, text = extract_lineid_phone(temp_path, debug=False)
    result = []
    if phone:
        result.append(f"手機號碼：{phone}")
    if lineid:
        result.append(f"LINE ID：{lineid}")
    if not result:
        result.append("未偵測到有效手機號碼或 LINE ID")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="\n".join(result))
    )
    import os
    os.remove(temp_path)
