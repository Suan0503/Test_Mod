from app.linebot_instance import line_bot_api
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction

def handle_follow(event):
    welcome_msg = (
        "歡迎加入🍵茗殿🍵\n"
        "\n"
        "請選擇驗證方式：\n"
        "1. 手動驗證\n"
        "2. 一鍵驗證\n"
        "\n"
        "※小助手無法預約，請洽專屬總機"
    )
    line_bot_api.push_message(
        event.source.user_id,
        TextSendMessage(
            text=welcome_msg,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="我同意規則", text="我同意規則"))
            ])
        )
    )
