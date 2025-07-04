from linebot.models import TextSendMessage
from extensions import line_bot_api
from utils.menu import get_menu_carousel  # 確保import正確路徑

def reply_with_menu(token, text=None):
    msgs = []
    if text:
        msgs.append(TextSendMessage(text=text))
    msgs.append(get_menu_carousel())
    line_bot_api.reply_message(token, msgs)
