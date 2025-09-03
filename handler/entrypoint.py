from extensions import handler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 匯入其他處理模組，確保其 @handler.add 被註冊
from . import verify  # noqa: F401
from . import menu    # noqa: F401
from . import report  # noqa: F401
from . import image   # noqa: F401
from . import follow  # noqa: F401


@handler.add(MessageEvent, message=TextMessage)
def echo_fallback(event):
	# 保底：避免沒有路由時無回應
	from extensions import line_bot_api
	line_bot_api.reply_message(event.reply_token, [
		TextSendMessage(text="請輸入正確指令或手機號碼")
	])
