from linebot.models import MessageEvent, TextMessage, TextSendMessage
from extensions import handler, line_bot_api, db
from models import Whitelist
from utils.temp_users import temp_users, manual_verify_pending
import random, string, time

# 管理員 ID 清單
ADMIN_IDS = ["你的管理員ID"]

def generate_verify_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# 驗證碼有效期（秒），例如 1 小時
VERIFY_CODE_EXPIRE = 86400

@handler.add(MessageEvent, message=TextMessage)
def handle_manual_verify(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    now_ts = int(time.time())

    # Step 1：管理員啟動手動驗證流程
    if user_text.startswith("手動驗證 - "):
        if user_id not in ADMIN_IDS:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 只有管理員可使用此功能"))
            return
        parts = user_text.split(" - ", 1)
        if len(parts) == 2:
            temp_users[user_id] = {"manual_step": "wait_lineid", "name": parts[1]}
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入該用戶的 LINE ID"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="格式錯誤，請用：手動驗證 - 暱稱"))
        return

    # Step 2：管理員輸入 LINE ID
    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_lineid":
        temp_users[user_id]['line_id'] = user_text
        temp_users[user_id]['manual_step'] = "wait_phone"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入該用戶的手機號碼"))
        return

    # Step 3：管理員輸入手機號，產生驗證碼
    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_phone":
        temp_users[user_id]['phone'] = user_text
        code = generate_verify_code()
        manual_verify_pending[code] = {
            'name': temp_users[user_id]['name'],
            'line_id': temp_users[user_id]['line_id'],
            'phone': temp_users[user_id]['phone'],
            'create_ts': now_ts,
            'admin_id': user_id,
            'step': 'wait_user_input'
        }
        del temp_users[user_id]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"驗證碼產生：{code}\n請將此8位驗證碼自行輸入聊天室")
        )
        return

    # Step 4：用戶輸入驗證碼
    if user_text in manual_verify_pending:
        info = manual_verify_pending[user_text]
        # 驗證碼有效期判斷
        if now_ts - info['create_ts'] > VERIFY_CODE_EXPIRE:
            del manual_verify_pending[user_text]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="驗證碼已過期，請重新申請。"))
            return
        # 新增白名單
        record = Whitelist.query.filter_by(phone=info['phone']).first()
        if record:
            # 已存在，補齊資料
            if not record.line_id:
                record.line_id = info['line_id']
            if not record.name:
                record.name = info['name']
            db.session.commit()
        else:
            # 新增
            record = Whitelist(
                phone=info['phone'],
                name=info['name'],
                line_id=info['line_id'],
                line_user_id=event.source.user_id
            )
            db.session.add(record)
            db.session.commit()
        # 成功通知
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=f"✅ 驗證成功，歡迎加入！\n暱稱：{info['name']}\nLINE ID：{info['line_id']}\n手機號：{info['phone']}"
        ))
        del manual_verify_pending[user_text]
        # 可加：通知管理員
        return

    # 管理員查詢待驗證名單
    if user_text == "查詢手動驗證":
        if user_id not in ADMIN_IDS:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 只有管理員可使用此功能"))
            return
        msg = "【待用戶輸入驗證碼名單】\n"
        for code, info in manual_verify_pending.items():
            msg += f"暱稱:{info['name']} LINE ID:{info['line_id']} 手機:{info['phone']} 驗證碼:{code}\n"
        if not manual_verify_pending:
            msg += "目前無待驗證名單"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
        return

    # 其他指令可擴充
