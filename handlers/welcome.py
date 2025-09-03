from linebot.models import FollowEvent, TextSendMessage

def register_welcome_handler(handler):
    @handler.add(FollowEvent)
    def handle_follow(event):
        welcome_text = (
            "歡迎加入🍵茗殿🍵\n"
            "請正確按照步驟提供資料配合快速驗證\n\n"
            "➡️ 請輸入手機號碼進行驗證（含09開頭）"
        )
        event.reply_token and event.source.user_id  # 確保 event 有 reply_token
        event.reply_token and handler.bot.reply_message(event.reply_token, TextSendMessage(text=welcome_text))
