
from linebot.models import TextSendMessage
from utils.cache import set_manual_pending, get_manual_pending, del_manual_pending, get_temp_user, set_temp_user
from utils.helper import generate_verify_code

ADMIN_IDS = [
    "U2bcd63000805da076721eb62872bc39f",
    "U5ce6c382d12eaea28d98f2d48673b4b8",
]

def handle_manual_verification(event, line_bot_api):
    user_id = event.source.user_id
    text = event.message.text.strip()

    # 僅限管理員可觸發手動驗證建立
    if user_id in ADMIN_IDS and text.startswith("手動驗證 - "):
        name = text.replace("手動驗證 - ", "")
        set_temp_user(user_id, {"manual_step": "wait_lineid", "name": name})
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入該用戶的 LINE ID"))
        return

    temp = get_temp_user(user_id)
    if not temp: return

    if temp.get("manual_step") == "wait_lineid":
        temp["line_id"] = text
        temp["manual_step"] = "wait_phone"
        set_temp_user(user_id, temp)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入該用戶的手機號碼"))
    elif temp.get("manual_step") == "wait_phone":
        temp["phone"] = text
        code = generate_verify_code()
        set_manual_pending(code, {
            "name": temp["name"],
            "line_id": temp["line_id"],
            "phone": temp["phone"]
        })
        del_temp_user(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"驗證碼產生：{code}"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請依正確順序操作～"))
