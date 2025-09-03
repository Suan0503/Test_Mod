from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
import os

db = SQLAlchemy()

# 回復為正式環境，不再覆寫 LineBotApi，取消所有 debug log
try:
	access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
	channel_secret = os.environ["LINE_CHANNEL_SECRET"]
	line_bot_api = LineBotApi(access_token)
	handler = WebhookHandler(channel_secret)
except KeyError:
	class _DummyLineBotApi:
		def __getattr__(self, name):
			def _noop(*args, **kwargs):
				print(f"[DummyLineBotApi] {name}", args, kwargs)
			return _noop

		# 常用方法明確定義（方便閱讀）
		def reply_message(self, *args, **kwargs):
			print("[DummyLineBotApi] reply_message", args, kwargs)

		def push_message(self, *args, **kwargs):
			print("[DummyLineBotApi] push_message", args, kwargs)

	class _DummyHandler:
		def add(self, *a, **kw):
			# 回傳 decorator（透傳）
			def decorator(func):
				print("[DummyHandler] add registered:", func.__name__)
				return func
			return decorator

		def handle(self, body, signature):
			print("[DummyHandler] handle called")

	line_bot_api = _DummyLineBotApi()
	handler = _DummyHandler()

