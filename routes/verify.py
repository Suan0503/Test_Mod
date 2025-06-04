from flask import abort
from linebot.models import TextSendMessage
from routes.ultis.cache import get_temp_user, set_temp_user, del_temp_user
from routes.ultis.helper import generate_verify_code

def handle_verification(event, line_bot_api):
    user_id = event.source.user_id
    text = event.message.text.strip()

    temp = get_temp_user(user_id) or {}

    if text.startswith("09") and len(text) == 10:
        temp["phone"] = text
        temp["step"] = "wait_id"
        set_temp_user(user_id, temp)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入您的 LINE ID（如無請輸入「尚未設定」）")
        )
    elif temp.get("step") == "wait_id":
        temp["line_id"] = text
        temp["step"] = "confirm"
        set_temp_user(user_id, temp)
        reply = f"""請確認以下資料是否正確：
📱手機：{temp['phone']}
🔗LINE ID：{temp['line_id']}
✅ 正確請輸入 1"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    elif temp.get("step") == "confirm" and text == "1":
        reply = f"""✅ 驗證成功囉！
📱手機：{temp['phone']}
🔗LINE ID：{temp['line_id']}"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        del_temp_user(user_id)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確的手機號碼（09開頭）進行驗證"))
