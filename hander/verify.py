from linebot.models import MessageEvent, TextMessage, TextSendMessage
from extensions import handler, line_bot_api, db
from models import Whitelist, Blacklist
from utils.menu_helpers import reply_with_menu
from utils.db_utils import update_or_create_whitelist_from_data
from utils.temp_users import temp_users, manual_verify_pending
from hander.admin import ADMIN_IDS
import random, string, re, time
from datetime import datetime
import pytz

def generate_verify_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

VERIFY_CODE_EXPIRE = 86400  # 驗證碼有效期（秒）

def normalize_phone(phone):
    phone = (phone or "").replace(" ", "").replace("-", "")
    if phone.startswith("+8869"):
        return "0" + phone[4:]
    if phone.startswith("+886"):
        return "0" + phone[4:]
    return phone

@handler.add(MessageEvent, message=TextMessage)
def handle_verify(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    tz = pytz.timezone("Asia/Taipei")
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception:
        display_name = "用戶"

    # ==== 管理員手動驗證流程（最高優先） ====
    if user_text.startswith("手動驗證 - "):
        if user_id not in ADMIN_IDS:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 只有管理員可使用此功能"))
            return
        parts = user_text.split(" - ", 1)
        if len(parts) == 2 and parts[1]:
            temp_users[user_id] = {"manual_step": "wait_lineid", "name": parts[1]}
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入該用戶的 LINE ID"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="格式錯誤，請用：手動驗證 - 暱稱"))
        return

    # Step 2: 管理員輸入 LINE ID
    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_lineid":
        if not user_text:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確的 LINE ID"))
            return
        temp_users[user_id]['line_id'] = user_text
        temp_users[user_id]['manual_step'] = "wait_phone"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入該用戶的手機號碼"))
        return

    # Step 3: 管理員輸入手機號並產生驗證碼
    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_phone":
        phone = normalize_phone(user_text)
        if not phone or not phone.startswith("09") or len(phone) != 10:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確的手機號碼（09xxxxxxxx）"))
            return
        temp_users[user_id]['phone'] = phone
        code = generate_verify_code()
        manual_verify_pending[code] = {
            'name': temp_users[user_id]['name'],
            'line_id': temp_users[user_id]['line_id'],
            'phone': temp_users[user_id]['phone'],
            'create_ts': int(time.time()),
            'admin_id': user_id,
            'step': 'wait_user_input'
        }
        del temp_users[user_id]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"驗證碼產生：{code}\n請將此8位驗證碼自行輸入聊天室")
        )
        return

    # Step 4: 用戶輸入驗證碼（管理員流程）
    if user_text in manual_verify_pending:
        info = manual_verify_pending[user_text]
        now_ts = int(time.time())
        if now_ts - info['create_ts'] > VERIFY_CODE_EXPIRE:
            del manual_verify_pending[user_text]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="驗證碼已過期，請重新申請。"))
            return
        # 新增或補全白名單
        record = Whitelist.query.filter_by(phone=info['phone']).first()
        if record:
            updated = False
            if not record.line_id:
                record.line_id = info['line_id']
                updated = True
            if not record.name:
                record.name = info['name']
                updated = True
            if updated:
                db.session.commit()
        else:
            record = Whitelist(
                phone=info['phone'],
                name=info['name'],
                line_id=info['line_id'],
                line_user_id=event.source.user_id
            )
            db.session.add(record)
            db.session.commit()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=f"✅ 驗證成功，歡迎加入！\n暱稱：{info['name']}\nLINE ID：{info['line_id']}\n手機號：{info['phone']}"
        ))
        del manual_verify_pending[user_text]
        return

    # Step 5: 管理員查詢待驗證名單
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

    # ==== 一般用戶自助驗證流程 ====
    # 正在進行圖片/LINE ID驗證
    if user_id in temp_users and temp_users[user_id].get("step") == "waiting_confirm":
        if user_text == "1":
            data = temp_users[user_id]
            now = datetime.now(tz)
            data["date"] = now.strftime("%Y-%m-%d")
            record, is_new = update_or_create_whitelist_from_data(data, user_id)
            if is_new:
                reply = (
                    f"📱 {data['phone']}\n"
                    f"🌸 暱稱：{data['name']}\n"
                    f"       個人編號：{record.id}\n"
                    f"🔗 LINE ID：{data['line_id']}\n"
                    f"🕒 {record.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                    f"✅ 驗證成功，歡迎加入茗殿\n"
                    f"🌟 加入密碼：ming666"
                )
            else:
                reply = (
                    f"📱 {record.phone}\n"
                    f"🌸 暱稱：{record.name or data.get('name')}\n"
                    f"       個人編號：{record.id}\n"
                    f"🔗 LINE ID：{record.line_id or data.get('line_id')}\n"
                    f"🕒 {record.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                    f"✅ 你的資料已補全，歡迎加入茗殿\n"
                    f"🌟 加入密碼：ming666"
                )
            reply_with_menu(event.reply_token, reply)
            temp_users.pop(user_id)
            return
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚠️ 如果資料正確請回覆 1，錯誤請重新輸入手機號碼。"))
            return

    # 已驗證用戶查詢
    existing = Whitelist.query.filter_by(line_user_id=user_id).first()
    if existing:
        if normalize_phone(user_text) == normalize_phone(existing.phone):
            reply = (
                f"📱 {existing.phone}\n"
                f"🌸 暱稱：{existing.name or display_name}\n"
                f"       個人編號：{existing.id}\n"
                f"🔗 LINE ID：{existing.line_id or '未登記'}\n"
                f"🕒 {existing.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"✅ 驗證成功，歡迎加入茗殿\n"
                f"🌟 加入密碼：ming666"
            )
            reply_with_menu(event.reply_token, reply)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚠️ 你已驗證完成，請輸入手機號碼查看驗證資訊"))
        return

    # 手機號碼驗證
    if re.match(r"^09\d{8}$", user_text):
        black = Blacklist.query.filter_by(phone=user_text).first()
        if black:
            return
        repeated = Whitelist.query.filter_by(phone=user_text).first()
        data = {"phone": user_text, "name": display_name}
        if repeated and repeated.line_user_id:
            update_or_create_whitelist_from_data(data)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ 此手機號碼已被使用，已補全缺失資料。")
            )
            return
        temp_users[user_id] = {"phone": user_text, "name": display_name, "step": "waiting_lineid"}
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="📱 手機已登記囉～請接著輸入您的 LINE ID"),
                TextSendMessage(
                    text=(
                        "若您有設定 LINE ID → ✅ 直接輸入即可\n"
                        "若尚未設定 ID → 請輸入：「尚未設定」\n"
                        "若您的 LINE ID 是手機號碼本身（例如 09xxxxxxxx）→ 請在開頭加上「ID」兩個字\n"
                        "例如：ID 0912345678"
                    )
                )
            ]
        )
        return

    # 填寫 LINE ID
    if user_id in temp_users and temp_users[user_id].get("step", "waiting_lineid") == "waiting_lineid" and len(user_text) >= 2:
        record = temp_users[user_id]
        input_lineid = user_text.strip()
        if input_lineid.lower().startswith("id"):
            phone_candidate = re.sub(r"[^\d]", "", input_lineid)
            if re.match(r"^id\s*09\d{8}$", input_lineid.lower().replace(" ", "")):
                record["line_id"] = phone_candidate
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ 請輸入正確格式：ID 09xxxxxxxx（例如：ID 0912345678）")
                )
                return
        elif input_lineid in ["尚未設定", "無ID", "無", "沒有", "未設定"]:
            record["line_id"] = "尚未設定"
        else:
            record["line_id"] = input_lineid
        record["step"] = "waiting_screenshot"
        temp_users[user_id] = record

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=(
                    "請上傳您的 LINE 個人頁面截圖（需清楚顯示手機號與 LINE ID）以供驗證。\n"
                    "📸 操作教學：LINE主頁 > 右上角設定 > 個人檔案（點進去之後截圖）"
                )
            )
        )
        return

    # 最後確認（for 圖片驗證流程）
    if user_text == "1" and user_id in temp_users and temp_users[user_id].get("step") == "waiting_confirm":
        data = temp_users[user_id]
        now = datetime.now(tz)
        data["date"] = now.strftime("%Y-%m-%d")
        record, is_new = update_or_create_whitelist_from_data(data, user_id)
        if is_new:
            reply = (
                f"📱 {data['phone']}\n"
                f"🌸 暱稱：{data['name']}\n"
                f"       個人編號：{record.id}\n"
                f"🔗 LINE ID：{data['line_id']}\n"
                f"🕒 {record.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"✅ 驗證成功，歡迎加入茗殿\n"
                f"🌟 加入密碼：ming666"
            )
        else:
            reply = (
                f"📱 {record.phone}\n"
                f"🌸 暱稱：{record.name or data.get('name')}\n"
                f"       個人編號：{record.id}\n"
                f"🔗 LINE ID：{record.line_id or data.get('line_id')}\n"
                f"🕒 {record.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"✅ 你的資料已補全，歡迎加入茗殿\n"
                f"🌟 加入密碼：ming666"
            )
        reply_with_menu(event.reply_token, reply)
        temp_users.pop(user_id)
        return

    # fallback
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入手機號碼進行驗證。"))
    return
