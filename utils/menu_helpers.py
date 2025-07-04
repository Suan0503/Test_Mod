from hander.image import get_function_menu_flex  # 你主選單 Flex function，若有更名請對應修改
from linebot.models import TextSendMessage
from extensions import line_bot_api

def reply_with_menu(token, text=None):
    """
    快速回覆主選單（可帶一段文字）。
    用法：reply_with_menu(event.reply_token, "xxx")
    """
    msgs = []
    if text:
        msgs.append(TextSendMessage(text=text))
    msgs.append(get_function_menu_flex())
    line_bot_api.reply_message(token, msgs)
