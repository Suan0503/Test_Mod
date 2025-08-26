"""
Follow 事件處理 (handle_follow)
- 處理用戶加入好友時的歡迎訊息
"""
from linebot.models import FollowEvent, TextSendMessage
import logging
from extensions import line_bot_api as _default_line_bot_api
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_follow(event, line_bot_api=None):
    api = line_bot_api or _default_line_bot_api
    msg = (
        "歡迎加入🍵茗殿🍵\n"
        "請正確按照步驟提供資料配合快速驗證\n\n"
        "➡️ 請輸入手機號碼進行驗證（含09開頭）"
    )
    try:
        api.reply_message(event.reply_token, TextSendMessage(text=msg))
    except Exception:
        logger.exception("回覆 FollowEvent 時發生錯誤")
