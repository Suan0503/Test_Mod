"""
驗證事件處理器 (handle_verify)
- 處理 LINE Bot 驗證流程、手動/自動驗證、OCR 驗證、管理員驗證等
"""
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, FollowEvent,
    QuickReply, QuickReplyButton, MessageAction, ImageSendMessage
)
from extensions import handler, line_bot_api, db
from models.blacklist import Blacklist
from models.whitelist import Whitelist
from utils.temp_users import temp_users
from storage import ADMIN_IDS
from utils.menu_helpers import reply_with_menu
from utils.db_utils import update_or_create_whitelist_from_data
import re, time, os, shutil, secrets, logging
from datetime import datetime, timedelta
import pytz
from PIL import Image
import pytesseract

# 驗證流程參數
VERIFY_CODE_EXPIRE = 900  # 驗證碼有效時間(秒)
OCR_DEBUG_IMAGE_BASEURL = os.getenv("OCR_DEBUG_IMAGE_BASEURL", "").rstrip("/")
OCR_DEBUG_IMAGE_DIR = os.getenv("OCR_DEBUG_IMAGE_DIR", "/tmp/ocr_debug")
manual_verify_pending = {}
admin_manual_flow = {}

# 工具函式

def normalize_phone(phone):
    phone = (phone or "").replace(" ", "").replace("-", "")
    if phone.startswith("+886"):
        return "0" + phone[4:]
    return phone

def make_qr(*labels_texts):
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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text, quick_reply=make_qr(*choices))
    )

def save_debug_image(temp_path, user_id):
    try:
        if not (OCR_DEBUG_IMAGE_BASEURL and OCR_DEBUG_IMAGE_DIR):
            return None
        os.makedirs(OCR_DEBUG_IMAGE_DIR, exist_ok=True)
        fname = f"{user_id}_{int(time.time())}.jpg"
        dest = os.path.join(OCR_DEBUG_IMAGE_DIR, fname)
        shutil.copyfile(temp_path, dest)
        return f"{OCR_DEBUG_IMAGE_BASEURL}/{fname}"
    except Exception:
        logging.exception("save_debug_image failed")
        return None

def generate_verification_code(length=8):
    return "".join(str(secrets.randbelow(10)) for _ in range(length))

def _find_pending_by_code(code):
    for key, pending in manual_verify_pending.items():
        if pending and pending.get("code") == code:
            return key, pending
    return None, None

# 主要驗證流程 (請依需求擴充)
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text.strip()
    user_id = event.source.user_id

    # 取得使用者暱稱
    profile = line_bot_api.get_profile(user_id)
    nickname = profile.display_name if profile else "使用者"

    # 管理員驗證流程
    if user_id in ADMIN_IDS:
        admin_flow = admin_manual_flow.get(user_id)
        if admin_flow:
            # ...existing admin flow code...
            return

    # 手動驗證流程
    pending_key, pending_data = _find_pending_by_code(text)
    if pending_key and pending_data:
        # ...existing manual verify code...
        return

    # 自動驗證流程
    # ...existing auto verify code...

    # 其他情況
    reply_basic(event, "無法識別的指令，請重新輸入或聯繫管理員協助。")
