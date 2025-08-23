from linebot.models import (
    FollowEvent, MessageEvent, TextMessage, ImageMessage,
    TextSendMessage, ImageSendMessage
)
from extensions import handler, line_bot_api, db
from models import Whitelist
from utils.temp_users import temp_users
from utils.menu_helpers import reply_with_menu
from utils.db_utils import update_or_create_whitelist_from_data
import os, time, re, pytz
from datetime import datetime
from PIL import Image
import pytesseract

# ─────────── 加入好友：發送歡迎訊息 ───────────
@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = (
        "歡迎加入🍵茗殿🍵\n"
        "請正確按照步驟提供資料配合快速驗證\n\n"
        "➡️ 請輸入手機號碼進行驗證（含09開頭）"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_msg))

# ─────────── Step1: 輸入手機 ───────────
@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    tz = pytz.timezone("Asia/Taipei")

    # Step1: 手機號碼
    if re.match(r"^09\d{8}$", user_text) and user_id not in temp_users:
        temp_users[user_id] = {"step": "waiting_lineid", "phone": user_text}
        line_bot_api.reply_message(event.reply_token, TextSendMessage("✅ 手機已記錄，請輸入您的 LINE ID（未設定請輸入：尚未設定）"))
        return

    # Step2: LINE ID
    if user_id in temp_users and temp_users[user_id].get("step") == "waiting_lineid":
        temp_users[user_id]["line_id"] = user_text
        temp_users[user_id]["step"] = "waiting_screenshot"
        line_bot_api.reply_message(event.reply_token, TextSendMessage("📸 請上傳您的 LINE 個人頁面截圖（需清楚顯示 LINE 名稱與 ID）"))
        return

# ─────────── Step3: 上傳截圖（OCR 判斷） ───────────
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id
    if user_id not in temp_users or temp_users[user_id].get("step") != "waiting_screenshot":
        return

    # 下載圖片
    message_content = line_bot_api.get_message_content(event.message.id)
    temp_path = f"/tmp/{user_id}_{int(time.time())}.jpg"
    with open(temp_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    # OCR
    try:
        img = Image.open(temp_path)
        ocr_text = pytesseract.image_to_string(img)
        expected_lineid = temp_users[user_id]["line_id"].lower()

        if expected_lineid in ["尚未設定", "未設定"]:
            match = True
        else:
            match = expected_lineid.lower() in ocr_text.lower()

        if match:
            # 寫入白名單
            data = temp_users[user_id]
            record, _ = update_or_create_whitelist_from_data(data, user_id)
            reply = (
                f"📱 {record.phone}\n"
                f"🌸 暱稱：{record.name or '用戶'}\n"
                f"🔗 LINE ID：{record.line_id or '未登記'}\n"
                f"🕒 {datetime.now(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"✅ 驗證成功，歡迎加入茗殿\n"
                f"🌟 加入密碼：ming666"
            )
            reply_with_menu(event.reply_token, reply)
            temp_users.pop(user_id, None)
        else:
            # 顯示 OCR 結果 & 圖片
            warn = (
                "⚠️ OCR 辨識結果與您輸入的 LINE ID 不符！\n"
                "以下為辨識文字供您檢查：\n\n"
                f"{ocr_text.strip() or '（未辨識出文字）'}"
            )
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=warn),
                    ImageSendMessage(
                        original_content_url="https://example.com/debug.jpg",  # 這裡換成實際對外網址
                        preview_image_url="https://example.com/debug.jpg"
                    )
                ]
            )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
