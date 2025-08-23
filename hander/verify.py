# -*- coding: utf-8 -*-
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, FollowEvent,
    QuickReply, QuickReplyButton, MessageAction, ImageSendMessage
)
from extensions import handler, line_bot_api, db
from models import Blacklist, Whitelist
from utils.temp_users import temp_users
from hander.admin import ADMIN_IDS
from utils.menu_helpers import reply_with_menu
from utils.db_utils import update_or_create_whitelist_from_data
import re, time, os, shutil
from datetime import datetime
import pytz
from PIL import Image
import pytesseract

# ─────────────────────────────────────────────────────────────────────────────
# 全域設定
# ─────────────────────────────────────────────────────────────────────────────
VERIFY_CODE_EXPIRE = 900  # 驗證碼有效時間(秒)
OCR_DEBUG_IMAGE_BASEURL = os.getenv("OCR_DEBUG_IMAGE_BASEURL", "").rstrip("/")  # 例: https://your.cdn.com/ocr
OCR_DEBUG_IMAGE_DIR = os.getenv("OCR_DEBUG_IMAGE_DIR", "/tmp/ocr_debug")        # 需自行以靜態伺服器對外提供

manual_verify_pending = {}

# ─────────────────────────────────────────────────────────────────────────────
# 小工具
# ─────────────────────────────────────────────────────────────────────────────
def normalize_phone(phone):
    phone = (phone or "").replace(" ", "").replace("-", "")
    if phone.startswith("+886"):
        # +8869xxxxxxxx 也會一起被處理
        return "0" + phone[4:]
    return phone

def make_qr(*labels_texts):
    """快速小工具：產生 QuickReply from tuples(label, text)"""
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label=lbl, text=txt))
        for (lbl, txt) in labels_texts
    ])

def reply_basic(event, text):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))

def reply_with_reverify(event, text):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=text,
            quick_reply=make_qr(("重新驗證", "重新驗證"))
        )
    )

def reply_with_choices(event, text, choices):
    # choices: list of (label, text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text, quick_reply=make_qr(*choices))
    )

def save_debug_image(temp_path, user_id):
    """
    可選：把使用者上傳的截圖搬到可對外讀取的目錄，並回傳完整 URL。
    需要你把 OCR_DEBUG_IMAGE_DIR 透過 Nginx/靜態空間對外對應到 OCR_DEBUG_IMAGE_BASEURL。
    若環境未設定，回傳 None（僅回 OCR 文字）。
    """
    try:
        if not (OCR_DEBUG_IMAGE_BASEURL and OCR_DEBUG_IMAGE_DIR):
            return None
        os.makedirs(OCR_DEBUG_IMAGE_DIR, exist_ok=True)
        fname = f"{user_id}_{int(time.time())}.jpg"
        dest = os.path.join(OCR_DEBUG_IMAGE_DIR, fname)
        shutil.copyfile(temp_path, dest)
        return f"{OCR_DEBUG_IMAGE_BASEURL}/{fname}"
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────────────────────
# 1) 加入好友：送歡迎訊息（你指定的文案）
# ─────────────────────────────────────────────────────────────────────────────
@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = (
        "歡迎加入🍵茗殿🍵\n"
        "請正確按照步驟提供資料配合快速驗證\n\n"
        "➡️ 請輸入手機號碼進行驗證（含09開頭）"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_msg))

# ─────────────────────────────────────────────────────────────────────────────
# 2) 文字訊息：手機 → LINE ID → 要截圖
#    同時保留你的查詢 / 管理路徑（可依需要調整）
# ─────────────────────────────────────────────────────────────────────────────
@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_id = event.source.user_id
    user_text = (event.message.text or "").strip()
    tz = pytz.timezone("Asia/Taipei")

    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception:
        display_name = "用戶"

    # 已驗證的用戶：阻止重驗並可回自身資訊
    existing = Whitelist.query.filter_by(line_user_id=user_id).first()
    if existing:
        if user_text == "重新驗證":
            reply_with_reverify(event, "您已通過驗證，無法重新驗證。")
            return
        # 若輸入同手機，回覆基本資訊＋菜單
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
            reply_with_reverify(event, "⚠️ 已驗證，若要查看資訊請輸入您當時驗證的手機號碼。")
        return

    # 查詢功能：維持原有（簡化版）
    if user_text.startswith("查詢 - "):
        phone = normalize_phone(user_text.replace("查詢 - ", "").strip())
        msg = f"查詢號碼：{phone}\n查詢結果："
        wl = Whitelist.query.filter_by(phone=phone).first()
        if wl:
            msg += " O白名單\n"
            msg += (
                f"暱稱：{wl.name}\n"
                f"LINE ID：{wl.line_id or '未登記'}\n"
                f"驗證時間：{wl.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
            )
        else:
            msg += " X白名單\n"
        bl = Blacklist.query.filter_by(phone=phone).first()
        if bl:
            msg += " O黑名單\n"
            msg += (
                f"暱稱：{bl.name}\n"
                f"LINE ID：{getattr(bl, 'line_id', '未登記')}\n"
                f"加入時間：{bl.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S') if hasattr(bl, 'created_at') and bl.created_at else '未紀錄'}\n"
            )
        else:
            msg += " X黑名單\n"
        reply_basic(event, msg)
        return

    # 「重新驗證」入口（未驗證者）
    if user_text == "重新驗證":
        temp_users[user_id] = {"step": "waiting_phone", "name": display_name, "reverify": True}
        reply_basic(event, "請輸入您的手機號碼（09開頭）開始重新驗證～")
        return

    # Step 1：若未在流程中，且訊息就是手機號 → 啟動驗證
    phone_candidate = normalize_phone(user_text)
    if user_id not in temp_users and re.match(r"^09\d{8}$", phone_candidate):
        # 黑名單擋
        if Blacklist.query.filter_by(phone=phone_candidate).first():
            reply_basic(event, "❌ 請聯絡管理員，無法自動通過驗證流程。")
            return
        # 已被其他 LINE 綁定擋
        owner = Whitelist.query.filter_by(phone=phone_candidate).first()
        if owner and owner.line_user_id and owner.line_user_id != user_id:
            reply_basic(event, "❌ 此手機已綁定其他帳號，請聯絡客服協助。")
            return

        temp_users[user_id] = {"step": "waiting_lineid", "name": display_name, "phone": phone_candidate}
        reply_basic(event, "✅ 手機號已登記～請輸入您的 LINE ID（未設定請輸入：尚未設定）")
        return

    # Step 1（已在流程中輸入手機）
    if user_id in temp_users and temp_users[user_id].get("step") == "waiting_phone":
        phone = normalize_phone(user_text)
        if not re.match(r"^09\d{8}$", phone):
            reply_basic(event, "⚠️ 請輸入正確的手機號碼（09開頭共10碼）")
            return
        if Blacklist.query.filter_by(phone=phone).first():
            reply_basic(event, "❌ 請聯絡管理員，無法自動通過驗證流程。")
            temp_users.pop(user_id, None)
            return
        owner = Whitelist.query.filter_by(phone=phone).first()
        if owner and owner.line_user_id and owner.line_user_id != user_id:
            reply_basic(event, "❌ 此手機已綁定其他帳號，請聯絡客服協助。")
            return

        temp_users[user_id]["phone"] = phone
        temp_users[user_id]["step"] = "waiting_lineid"
        reply_basic(event, "✅ 手機號已登記～請輸入您的 LINE ID（未設定請輸入：尚未設定）")
        return

    # Step 2：輸入 LINE ID
    if user_id in temp_users and temp_users[user_id].get("step") == "waiting_lineid":
        line_id = user_text.strip()
        if not line_id:
            reply_basic(event, "⚠️ 請輸入有效的 LINE ID（或輸入：尚未設定）")
            return
        temp_users[user_id]["line_id"] = line_id
        temp_users[user_id]["step"] = "waiting_screenshot"
        reply_basic(
            event,
            "📸 請上傳您的 LINE 個人頁面截圖\n"
            "👉 路徑：LINE主頁 > 右上角設定 > 個人檔案 > 點進去後截圖\n"
            "需清楚顯示 LINE 名稱與（若有）ID，作為驗證依據"
        )
        return

    # fallback：不是指令也不是流程，提示啟動驗證
    if user_id not in temp_users:
        temp_users[user_id] = {"step": "waiting_phone", "name": display_name}
        reply_basic(event, "歡迎～請直接輸入手機號碼（09開頭）進行驗證。")
        return

# ─────────────────────────────────────────────────────────────────────────────
# 3) 圖片訊息：OCR → 快速通關 / 資料有誤 顯示 OCR 圖片(或文字)
#    規則：若使用者 LINE ID ≠「尚未設定」且 OCR 文字包含該 ID → 直接通過
#          否則顯示 OCR 結果與(可選)圖片預覽，提供「重新上傳 / 我確定正確(1)」
# ─────────────────────────────────────────────────────────────────────────────
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id
    if user_id not in temp_users or temp_users[user_id].get("step") != "waiting_screenshot":
        reply_with_reverify(event, "請先完成前面步驟後再上傳截圖唷～")
        return

    # 儲存圖片檔
    message_content = line_bot_api.get_message_content(event.message.id)
    tmp_dir = "/tmp/ocr_inbox"
    os.makedirs(tmp_dir, exist_ok=True)
    temp_path = os.path.join(tmp_dir, f"{user_id}_{int(time.time())}.jpg")
    with open(temp_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    expected_line_id = (temp_users[user_id].get("line_id") or "").strip()
    try:
        image = Image.open(temp_path)
        # 提高容錯：不指定語言，避免多語系/字母大小寫出問題
        ocr_text = pytesseract.image_to_string(image)
        ocr_text_low = (ocr_text or "").lower()

        def fast_pass():
            # 完成通關與入庫
            tz = pytz.timezone("Asia/Taipei")
            data = temp_users[user_id]
            now = datetime.now(tz)
            data["date"] = now.strftime("%Y-%m-%d")
            record, _ = update_or_create_whitelist_from_data(
                data, user_id, reverify=temp_users[user_id].get("reverify", False)
            )
            reply = (
                f"📱 {record.phone}\n"
                f"🌸 暱稱：{record.name or '用戶'}\n"
                f"🔗 LINE ID：{record.line_id or '未登記'}\n"
                f"🕒 {record.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"✅ 驗證成功，歡迎加入茗殿\n"
                f"🌟 加入密碼：ming666"
            )
            reply_with_menu(event.reply_token, reply)
            temp_users.pop(user_id, None)

        # 1) 若 LINE ID 為「尚未設定」：不做比對，直接讓用戶通關
        if expected_line_id in ["尚未設定", "未設定", "無", "none", "not set"]:
            fast_pass()
            return

        # 2) 正常快速通關：OCR 文字包含 LINE ID（不分大小寫）
        if expected_line_id and expected_line_id.lower() in ocr_text_low:
            fast_pass()
            return

        # 3) 資料對不上：顯示 OCR 結果＋（可選）圖片預覽
        public_url = save_debug_image(temp_path, user_id)
        preview_note = ""
        preview_msg = []
        if public_url:
            preview_note = "\n📷 這是我們辨識用的截圖預覽（僅你可見）："
            preview_msg.append(ImageSendMessage(original_content_url=public_url, preview_image_url=public_url))

        warn = (
            "⚠️ 截圖中的內容無法對上您剛輸入的 LINE ID。\n"
            "以下是 OCR 辨識到的重點文字（供你核對）：\n"
            "——— OCR ———\n"
            f"{ocr_text.strip()[:900] or '（無文字或辨識失敗）'}\n"
            "———————\n"
            "若資料正確請點「我確定正確(1)」，或點「重新上傳」再傳一張更清晰的截圖。"
            f"{preview_note}"
        )
        # 設定：進入等待確認，讓用戶可以強制通過（維持三步驗證體感）
        temp_users[user_id]["step"] = "waiting_confirm_after_ocr"
        text_msg = TextSendMessage(
            text=warn,
            quick_reply=make_qr(("重新上傳", "重新上傳"), ("我確定正確(1)", "1"))
        )
        if preview_msg:
            line_bot_api.reply_message(event.reply_token, [text_msg] + preview_msg)
        else:
            line_bot_api.reply_message(event.reply_token, text_msg)

    except Exception:
        reply_with_reverify(event, "⚠️ 圖片處理失敗，請重新上傳或改由客服協助。")
    finally:
        # 保留本地檔僅作暫存（若有對外預覽已另存）
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

# ─────────────────────────────────────────────────────────────────────────────
# 4) OCR 不一致→使用者仍可回「1」強制確認通過；或回「重新上傳」
# ─────────────────────────────────────────────────────────────────────────────
@handler.add(MessageEvent, message=TextMessage)
def handle_post_ocr_confirm(event):
    user_id = event.source.user_id
    user_text = (event.message.text or "").strip()
    tz = pytz.timezone("Asia/Taipei")

    # 重新上傳截圖
    if user_id in temp_users and temp_users[user_id].get("step") in ("waiting_screenshot", "waiting_confirm_after_ocr") and user_text == "重新上傳":
        temp_users[user_id]["step"] = "waiting_screenshot"
        reply_basic(event, "請重新上傳您的 LINE 個人頁面截圖（個人檔案按進去後請直接截圖）。")
        return

    # 使用者確認「1」：通過
    if user_id in temp_users and temp_users[user_id].get("step") == "waiting_confirm_after_ocr" and user_text == "1":
        data = temp_users[user_id]
        now = datetime.now(tz)
        data["date"] = now.strftime("%Y-%m-%d")
        record, _ = update_or_create_whitelist_from_data(
            data, user_id, reverify=temp_users[user_id].get("reverify", False)
        )
        reply = (
            f"📱 {record.phone}\n"
            f"🌸 暱稱：{record.name or '用戶'}\n"
            f"🔗 LINE ID：{record.line_id or '未登記'}\n"
            f"🕒 {record.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
            f"✅ 驗證成功，歡迎加入茗殿\n"
            f"🌟 加入密碼：ming666"
        )
        reply_with_menu(event.reply_token, reply)
        temp_users.pop(user_id, None)
        return

# ---- 新增：供 hander.entrypoint import 使用的 wrapper ----
def handle_verify(event):
    """
    Entrypoint wrapper：hander.entrypoint 會呼叫這個函式
    根據 event 的類型分派到 verify 模組中的處理函式。
    這是為了解決 'cannot import name handle_verify' 的導入錯誤。
    """
    try:
        # 若是 MessageEvent 且有 message 屬性，根據 message 類型分派
        if hasattr(event, "message") and event.message is not None:
            msg = event.message
            # TextMessage -> 呼叫 handle_text
            if isinstance(msg, TextMessage):
                return handle_text(event)
            # ImageMessage -> 呼叫 handle_image
            if isinstance(msg, ImageMessage):
                return handle_image(event)
        # FollowEvent -> 呼叫 handle_follow
        if isinstance(event, FollowEvent):
            return handle_follow(event)
        # 其他情況：嘗試由文字處理接管
        return handle_text(event)
    except Exception:
        # 紀錄 exception（避免 silent fail）
        import logging
        logging.exception("handle_verify dispatch failed")
        # 若需要也可以回覆使用者一條友善的錯誤訊息
        try:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="系統發生錯誤，請稍後再試或聯絡管理員。"))
        except Exception:
            pass
        raise
