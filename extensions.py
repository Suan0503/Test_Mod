from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
import os

db = SQLAlchemy()

class DebugLineBotApi(LineBotApi):
    def reply_message(self, *args, **kwargs):
        import traceback
        print("=== [DEBUG] reply_message 被呼叫 ===")
        print("args:", args)
        print("kwargs:", kwargs)
        traceback.print_stack()
        return super().reply_message(*args, **kwargs)
    def push_message(self, *args, **kwargs):
        print("=== [DEBUG] push_message 被呼叫 ===")
        print("args:", args)
        print("kwargs:", kwargs)
        return super().push_message(*args, **kwargs)

line_bot_api = DebugLineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
