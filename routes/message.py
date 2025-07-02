from flask import Blueprint, request, abort, jsonify
from extensions import line_bot_api, handler, db
from linebot.models import (
    MessageEvent, TextMessage, FlexSendMessage, FollowEvent, ImageMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent
)
from linebot.exceptions import InvalidSignatureError
from datetime import datetime
import pytz
import os
import re
import random
import string
import traceback
import time

from models import Whitelist, Blacklist, Coupon
from utils.draw_utils import draw_coupon, get_today_coupon_flex, has_drawn_today, save_coupon_record
from utils.image_verification import extract_lineid_phone
from utils.special_case import is_special_case
from utils.menu import get_menu_carousel
from storage import ADMIN_IDS, temp_users, manual_verify_pending

# 新增：跨請求暫存回報文資料
report_pending_map = {}

message_bp = Blueprint('message', __name__)

def generate_verify_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def choose_link():
    group = [
        "https://line.me/ti/p/g7TPO_lhAL",
        "https://line.me/ti/p/Q6-jrvhXbH",
        "https://line.me/ti/p/AKRUvSCLRC"
    ]
    return group[hash(os.urandom(8)) % len(group)]

def update_or_create_whitelist_from_data(data, user_id=None):
    existing = Whitelist.query.filter_by(phone=data["phone"]).first()
    need_commit = False
    if existing:
        if data.get("name") and (not existing.name):
            existing.name = data["name"]
            need_commit = True
        if data.get("line_id") and (not existing.line_id):
            existing.line_id = data["line_id"]
            need_commit = True
        if user_id and (not existing.line_user_id):
            existing.line_user_id = user_id
            need_commit = True
        if data.get("reason") and (not existing.reason):
            existing.reason = data["reason"]
            need_commit = True
        if data.get("date") and (not existing.date):
            existing.date = data["date"]
            need_commit = True
        if need_commit:
            db.session.commit()
        return existing, False
    else:
        new_user = Whitelist(
            phone=data["phone"],
            name=data.get("name"),
            line_id=data.get("line_id"),
            line_user_id=user_id if user_id else data.get("line_user_id"),
            reason=data.get("reason"),
            date=data.get("date"),
            created_at=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user, True

def normalize_phone(phone):
    """將手機號碼轉為09開頭格式"""
    phone = (phone or "").replace(" ", "").replace("-", "")
    if phone.startswith("+8869"):
        return "0" + phone[4:]
    if phone.startswith("+886"):
        return "0" + phone[4:]
    return phone

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

@handler.add(FollowEvent)
def handle_follow(event):
    msg = (
        "歡迎加入🍵茗殿🍵\n"
        "請正確按照步驟提供資料配合快速驗證\n\n"
        "➡️ 請輸入手機號碼進行驗證（含09開頭）"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    tz = pytz.timezone("Asia/Taipei")
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception as e:
        print(f"取得用戶 {user_id} profile 失敗：{e}")
        display_name = "用戶"

    # === 回報文流程 ===
    if user_text in ["回報文", "Report", "report"]:
        temp_users[user_id] = {"report_pending": True}
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入要回報的網址（請直接貼網址）：")
        )
        return

    if user_id in temp_users and temp_users[user_id].get("report_pending"):
        url = user_text
        if not re.match(r"^https?://", url):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入正確的網址格式（必須以 http:// 或 https:// 開頭）")
            )
            return
        # 取得用戶資料
        wl = Whitelist.query.filter_by(line_user_id=user_id).first()
        user_number = wl.id if wl else ""
        user_lineid = wl.line_id if wl else ""

        # ButtonsTemplate text 最多60字，這裡只放網址或提示
        short_text = f"網址：{url}" if len(url) < 55 else "新回報文，請點選按鈕處理"
        # 詳細內容另發一則文字
        detail_text = (
            f"【用戶回報文】\n"
            f"暱稱：{display_name}\n"
            f"用戶編號：{user_number}\n"
            f"LINE ID：{user_lineid}\n"
            f"網址：{url}"
        )
        report_id = f"{user_id}_{int(time.time()*1000)}"
        for admin_id in ADMIN_IDS:
            report_pending_map[report_id] = {
                "user_id": user_id,
                "admin_id": admin_id,
                "display_name": display_name,
                "user_number": user_number,
                "user_lineid": user_lineid,
                "url": url
            }
            # 發送審核按鈕
            line_bot_api.push_message(
                admin_id,
                TemplateSendMessage(
                    alt_text="收到用戶回報文",
                    template=ButtonsTemplate(
                        title="收到新回報文",
                        text=short_text,
                        actions=[
                            PostbackAction(label="🟢 O", data=f"report_ok|{report_id}"),
                            PostbackAction(label="❌ X", data=f"report_ng|{report_id}")
                        ]
                    )
                )
            )
            # 另外發詳細資料
            line_bot_api.push_message(admin_id, TextSendMessage(text=detail_text))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="✅ 已收到您的回報，管理員會盡快處理！")
        )
        temp_users.pop(user_id)
        return

    # 管理員輸入拒絕原因
    if user_id in temp_users and temp_users[user_id].get("report_ng_pending"):
        report_id = temp_users[user_id]["report_ng_pending"]
        info = report_pending_map.get(report_id)
        if info:
            reason = user_text
            to_user_id = info["user_id"]
            reply = f"❌ 您的回報文未通過審核，原因如下：\n{reason}"
            try:
                line_bot_api.push_message(to_user_id, TextSendMessage(text=reply))
            except Exception as e:
                print("推播用戶回報拒絕失敗", e)
            temp_users.pop(user_id)
            report_pending_map.pop(report_id, None)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已將原因回傳給用戶。"))
        else:
            temp_users.pop(user_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到該回報資料（可能已處理過或超時）"))
        return

    # 主選單指令
    if user_text in ["主選單", "功能選單", "選單", "menu", "Menu"]:
        line_bot_api.reply_message(event.reply_token, get_menu_carousel())
        return

    # === 呼叫管理員功能 ===
    if user_text in ["呼叫管理員", "聯絡管理員", "聯繫管理員", "找管理員"]:
        wl = Whitelist.query.filter_by(line_user_id=user_id).first()
        user_number = wl.id if wl else ""
        user_lineid = wl.line_id if wl else ""
        notify_text = (
            f"【用戶呼叫管理員】\n"
            f"暱稱：{display_name}\n"
            f"用戶編號：{user_number}\n"
            f"LINE ID：{user_lineid}\n"
            f"訊息：{user_text}\n\n"
            f"➡️ 若要私訊此用戶，請輸入：/msg {user_id} 你的回覆內容"
        )
        for admin_id in ADMIN_IDS:
            try:
                line_bot_api.push_message(admin_id, TextSendMessage(text=notify_text))
            except Exception as e:
                print(f"推播給管理員 {admin_id} 失敗：", e)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ 已通知管理員，請稍候協助！"))
        return

    # === 管理員私訊用戶：/msg <user_id> <內容> ===
    if user_id in ADMIN_IDS and user_text.startswith("/msg "):
        try:
            parts = user_text.split(" ", 2)
            if len(parts) < 3:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="格式錯誤，請用 /msg <user_id> <內容>"))
                return
            target_user_id = parts[1].strip()
            msg = parts[2].strip()
            line_bot_api.push_message(target_user_id, TextSendMessage(text=f"【管理員回覆】\n{msg}"))
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已發送訊息給用戶"))
        except Exception as e:
            print("管理員私訊失敗：", e)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發送失敗，請檢查 user_id 是否正確"))
        return

    # === 手動驗證 - 僅限管理員流程 ===
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

    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_lineid":
        temp_users[user_id]['line_id'] = user_text
        temp_users[user_id]['manual_step'] = "wait_phone"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入該用戶的手機號碼"))
        return

    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_phone":
        temp_users[user_id]['phone'] = user_text
        code = generate_verify_code()
        manual_verify_pending[code] = {
            'name': temp_users[user_id]['name'],
            'line_id': temp_users[user_id]['line_id'],
            'phone': temp_users[user_id]['phone'],
            'step': 'wait_user_input'
        }
        del temp_users[user_id]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"驗證碼產生：{code}\n請將此8位驗證碼自行輸入聊天室")
        )
        return

    if len(user_text) == 8 and user_text in manual_verify_pending:
        record = manual_verify_pending[user_text]
        temp_users[user_id] = {
            "manual_step": "wait_confirm",
            "name": record['name'],
            "line_id": record['line_id'],
            "phone": record['phone'],
            "verify_code": user_text
        }
        reply = (
            f"📱 手機號碼：{record['phone']}\n"
            f"🌸 暱稱：{record['name']}\n"
            f"       個人編號：待驗證後產生\n"
            f"🔗 LINE ID：{record['line_id']}\n"
            f"（此用戶為手動通過）\n"
            f"請問以上資料是否正確？正確請回復 1\n"
            f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        manual_verify_pending.pop(user_text, None)
        return

    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_confirm" and user_text == "1":
        data = temp_users[user_id]
        now = datetime.now(tz)
        data["date"] = now.strftime("%Y-%m-%d")
        record, is_new = update_or_create_whitelist_from_data(data, user_id)
        if is_new:
            reply = (
                f"📱 手機號碼：{data['phone']}\n"
                f"🌸 暱稱：{data['name']}\n"
                f"       個人編號：{record.id}\n"
                f"🔗 LINE ID：{data['line_id']}\n"
                f"✅ 驗證成功，歡迎加入茗殿"
            )
        else:
            reply = (
                f"📱 手機號碼：{record.phone}\n"
                f"🌸 暱稱：{record.name or data.get('name')}\n"
                f"       個人編號：{record.id}\n"
                f"🔗 LINE ID：{record.line_id or data.get('line_id')}\n"
                f"✅ 你的資料已補全，歡迎加入茗殿"
            )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        temp_users.pop(user_id)
        return

    if user_text == "手動通過":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 此功能已關閉"))
        return

    if user_text == "驗證資訊":
        existing = Whitelist.query.filter_by(line_user_id=user_id).first()
        if existing:
            tz = pytz.timezone("Asia/Taipei")
            reply = (
                f"📱 {existing.phone}\n"
                f"🌸 暱稱：{existing.name or display_name}\n"
                f"       個人編號：{existing.id}\n"
                f"🔗 LINE ID：{existing.line_id or '未登記'}\n"
                f"🕒 {existing.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"✅ 驗證成功，歡迎加入茗殿\n"
                f"🌟 加入密碼：ming666"
            )
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply), get_menu_carousel()])
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚠️ 你尚未完成驗證，請輸入手機號碼進行驗證。"))
        return

    if user_text == "每日抽獎":
        if not Whitelist.query.filter_by(line_user_id=user_id).first():
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚠️ 你尚未完成驗證，請先完成驗證才能參加每日抽獎！"))
            return

        today_str = datetime.now(tz).strftime("%Y-%m-%d")
        if has_drawn_today(user_id, Coupon):
            coupon = Coupon.query.filter_by(line_user_id=user_id, date=today_str).first()
            flex = get_today_coupon_flex(user_id, display_name, coupon.amount)
            line_bot_api.reply_message(event.reply_token, flex)
            return
        amount = draw_coupon()
        save_coupon_record(user_id, amount, Coupon, db)
        flex = get_today_coupon_flex(user_id, display_name, amount)
        line_bot_api.reply_message(event.reply_token, flex)
        return

    existing = Whitelist.query.filter_by(line_user_id=user_id).first()
    if existing:
        if normalize_phone(user_text) == normalize_phone(existing.phone):
            tz = pytz.timezone("Asia/Taipei")
            reply = (
                f"📱 {existing.phone}\n"
                f"🌸 暱稱：{existing.name or display_name}\n"
                f"       個人編號：{existing.id}\n"
                f"🔗 LINE ID：{existing.line_id or '未登記'}\n"
                f"🕒 {existing.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"✅ 驗證成功，歡迎加入茗殿\n"
                f"🌟 加入密碼：ming666"
            )
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply), get_menu_carousel()])
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚠️ 你已驗證完成，請輸入手機號碼查看驗證資訊"))
        return

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

    if user_id in temp_users and temp_users[user_id].get("step", "waiting_lineid") == "waiting_lineid" and len(user_text) >= 2:
        record = temp_users[user_id]
        input_lineid = user_text.strip()
        if input_lineid.lower().startswith("id"):
            phone_candidate = re.sub(r"[^\d]", "", input_lineid)
            # 必須有 ID+空白+09xxxxxxxx 共至少12字元
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
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply), get_menu_carousel()])
        temp_users.pop(user_id)
        return

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data = event.postback.data
    # report_ok|{report_id}
    if data.startswith("report_ok|"):
        report_id = data.split("|")[1]
        info = report_pending_map.get(report_id)
        if info:
            to_user_id = info["user_id"]
            reply = "🟢 您的回報文已審核通過，獲得一張月底抽獎券！"
            # 新增：給用戶一張抽獎券資料庫記錄
            try:
                tz = pytz.timezone("Asia/Taipei")
                today = datetime.now(tz).strftime("%Y-%m-%d")
                new_coupon = Coupon(
                    line_user_id=to_user_id,
                    amount=1,  # 你可以視需求自訂 amount
                    date=today,
                    created_at=datetime.now(tz)
                )
                db.session.add(new_coupon)
                db.session.commit()
                line_bot_api.push_message(to_user_id, TextSendMessage(text=reply))
            except Exception as e:
                print("推播用戶通過回報文失敗", e)
            report_pending_map.pop(report_id, None)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已通過並回覆用戶。"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="該回報已處理過或超時"))
        return
    elif data.startswith("report_ng|"):
        report_id = data.split("|")[1]
        info = report_pending_map.get(report_id)
        if info:
            temp_users[user_id] = {"report_ng_pending": report_id}
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入不通過的原因："))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="該回報已處理過或超時"))
        return

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id
    if user_id not in temp_users or temp_users[user_id].get("step") != "waiting_screenshot":
        return

    if is_special_case(user_id):
        record = temp_users[user_id]
        reply = (
            f"📱 {record['phone']}\n"
            f"🌸 暱稱：{record['name']}\n"
            f"       個人編號：待驗證後產生\n"
            f"🔗 LINE ID：{record['line_id']}\n"
            f"（此用戶經手動通過）\n"
            f"請問以上資料是否正確？正確請回復 1\n"
            f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
        )
        record["step"] = "waiting_confirm"
        temp_users[user_id] = record
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    image_path = f"/tmp/{user_id}_line_profile.png"
    with open(image_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    phone_ocr, lineid_ocr, ocr_text = extract_lineid_phone(image_path)
    input_phone = temp_users[user_id].get("phone")
    input_lineid = temp_users[user_id].get("line_id")
    record = temp_users[user_id]

    # OCR與手動輸入完全吻合則自動通關
    if (
        phone_ocr and lineid_ocr
        and normalize_phone(phone_ocr) == normalize_phone(input_phone)
        and input_lineid is not None and lineid_ocr.lower() == input_lineid.lower()
    ):
        tz = pytz.timezone("Asia/Taipei")
        now = datetime.now(tz)
        record["date"] = now.strftime("%Y-%m-%d")
        whitelist_record, is_new = update_or_create_whitelist_from_data(record, user_id)
        reply = (
            f"📱 {record['phone']}\n"
            f"🌸 暱稱：{record['name']}\n"
            f"       個人編號：{whitelist_record.id}\n"
            f"🔗 LINE ID：{record['line_id']}\n"
            f"🕒 {whitelist_record.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
            f"✅ 驗證成功，歡迎加入茗殿\n"
            f"🌟 加入密碼：ming666"
        )
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply), get_menu_carousel()])
        temp_users.pop(user_id, None)
        return

    if input_lineid == "尚未設定":
        if normalize_phone(phone_ocr) == normalize_phone(input_phone):
            reply = (
                f"📱 {record['phone']}\n"
                f"🌸 暱稱：{record['name']}\n"
                f"       個人編號：待驗證後產生\n"
                f"🔗 LINE ID：尚未設定\n"
                f"請問以上資料是否正確？正確請回復 1\n"
                f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
            )
            record["step"] = "waiting_confirm"
            temp_users[user_id] = record
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ 截圖中的手機號碼與您輸入的不符，請重新上傳正確的 LINE 個人頁面截圖。")
            )
    else:
        lineid_match = (lineid_ocr is not None and input_lineid is not None and lineid_ocr.lower() == input_lineid.lower())
        if normalize_phone(phone_ocr) == normalize_phone(input_phone) and (lineid_match or lineid_ocr == "尚未設定"):
            reply = (
                f"📱 {record['phone']}\n"
                f"🌸 暱稱：{record['name']}\n"
                f"       個人編號：待驗證後產生\n"
                f"🔗 LINE ID：{record['line_id']}\n"
                f"請問以上資料是否正確？正確請回復 1\n"
                f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
            )
            record["step"] = "waiting_confirm"
            temp_users[user_id] = record
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=(
                        "❌ 截圖中的手機號碼或 LINE ID 與您輸入的不符，請重新上傳正確的 LINE 個人頁面截圖。\n"
                        f"【圖片偵測結果】手機:{phone_ocr or '未識別'}\nLINE ID:{lineid_ocr or '未識別'}"
                    )
                )
            )

@message_bp.route("/ocr", methods=["POST"])
def ocr_image_verification():
    if "image" not in request.files:
        return jsonify({"error": "請上傳圖片（欄位名稱 image）"}), 400
    file = request.files["image"]
    file_path = "temp_ocr_img.png"
    file.save(file_path)
    phone, line_id, text = extract_lineid_phone(file_path)
    os.remove(file_path)
    return jsonify({
        "phone": phone,
        "line_id": line_id,
        "ocr_text": text
    })
