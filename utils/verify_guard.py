"""
驗證守門工具
"""
from models.whitelist import Whitelist
from linebot.models import TextSendMessage

def is_verified(user_id):
    return Whitelist.query.filter_by(line_user_id=user_id).first() is not None

def guard_verified(event, line_bot_api):
    user_id = event.source.user_id
    if not is_verified(user_id):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=(
                    "⚠️ 你尚未完成驗證，請輸入手機號碼進行驗證。\n\n"
                    "請於聊天視窗輸入您的手機號碼（例：0912345678），"
                    "將會收到驗證流程指示。"
                )
            )
        )
        return False
    return True
