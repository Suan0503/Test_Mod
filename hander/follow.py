from extensions import line_bot_api
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction

def handle_follow(event):
    user_id = event.source.user_id
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception:
        display_name = "用戶"
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="我同意規則", text="我同意規則")),
        QuickReplyButton(action=MessageAction(label="重新驗證", text="重新驗證"))
    ])
    line_bot_api.push_message(
        user_id,
        TextSendMessage(
            text=f"歡迎 {display_name}，請選擇驗證方式：",
            quick_reply=quick_reply
        )
    )
