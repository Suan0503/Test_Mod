import re
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
from linebot import LineBotApi
from services.verify_service import process_verification, process_ocr_image
from utils.validators import is_valid_phone, is_valid_lineid
from flask import current_app
from utils.temp_users import get_temp_user, set_temp_user, clear_temp_user
from templates.verify_messages import ASK_LINEID, ASK_SCREENSHOT, INVALID_PHONE, INVALID_LINEID, VERIFY_SUCCESS

# LINE BOT 驗證流程入口

def register_verify_handlers(handler):
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text(event):
        user_id = event.source.user_id
        text = event.message.text.strip()
        temp = get_temp_user(user_id)
        if not temp:
            if is_valid_phone(text):
                set_temp_user(user_id, {"step": "waiting_lineid", "phone": text})
                event.reply_token and handler.bot.reply_message(event.reply_token, TextSendMessage(text=ASK_LINEID))
            else:
                event.reply_token and handler.bot.reply_message(event.reply_token, TextSendMessage(text=INVALID_PHONE))
            return
        if temp.get("step") == "waiting_lineid":
            if is_valid_lineid(text):
                temp["line_id"] = text
                temp["step"] = "waiting_screenshot"
                set_temp_user(user_id, temp)
                event.reply_token and handler.bot.reply_message(event.reply_token, TextSendMessage(text=ASK_SCREENSHOT))
            else:
                event.reply_token and handler.bot.reply_message(event.reply_token, TextSendMessage(text=INVALID_LINEID))
            return
        if temp.get("step") == "waiting_screenshot":
            event.reply_token and handler.bot.reply_message(event.reply_token, TextSendMessage(text="請上傳截圖圖片（LINE個人頁面）"))
            return

    @handler.add(MessageEvent, message=ImageMessage)
    def handle_image(event):
        user_id = event.source.user_id
        temp = get_temp_user(user_id)
        if temp and temp.get("step") == "waiting_screenshot":
            # OCR 處理
            ocr_text = process_ocr_image(event)
            clear_temp_user(user_id)
            event.reply_token and handler.bot.reply_message(event.reply_token, TextSendMessage(text=VERIFY_SUCCESS + f"\nOCR結果：{ocr_text}"))
        else:
            event.reply_token and handler.bot.reply_message(event.reply_token, TextSendMessage(text="請依流程操作，先輸入手機號碼與LINE ID。"))
