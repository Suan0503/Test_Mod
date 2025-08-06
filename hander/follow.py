from linebot.models import FollowEvent, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from extensions import handler, line_bot_api

@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = (
        "歡迎加入🍵茗殿🍵\n"
        "請詳閱以下規則並同意後開始驗證：\n"
        "1. 請輸入正確手機號碼（09開頭）\n"
        "2. LINE ID 如未設定請輸入『尚未設定』\n"
        "3. 請上傳LINE個人頁截圖\n"
        "4. 禁止惡意操作，違者永久封鎖\n"
        "\n請點擊下方『我同意規則』開始驗證。"
    )
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=welcome_msg,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="我同意規則", text="我同意規則"))
            ])
        )
    )
