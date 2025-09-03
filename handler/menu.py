from extensions import handler, line_bot_api
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from utils.menu_helpers import reply_with_menu, get_menu_carousel
from models import Whitelist
from .verify import build_student_card_flex


@handler.add(MessageEvent, message=TextMessage)
def handle_menu(event):
	text = event.message.text.strip()
	if text in ["主選單", "menu", "Menu"]:
		reply_with_menu(event.reply_token)
		return
	if text in ["驗證資訊", "我的資訊", "我的資料"]:
		wl = Whitelist.query.filter_by(line_id=event.source.user_id).first()
		if wl:
			flex = build_student_card_flex(
				phone=wl.phone or "",
				nickname=wl.name or "",
				number=getattr(wl, 'student_no', '') or str(wl.id or ''),
				lineid=wl.line_id or "",
				join_code=getattr(wl, 'join_code', '') or str(wl.id or ''),
				time_str=(wl.created_at.strftime("%Y-%m-%d %H:%M") if getattr(wl, 'created_at', None) else ""),
				avatar_url=None,
			)
			msgs = [FlexSendMessage(alt_text="驗證資訊", contents=flex), get_menu_carousel()]
			line_bot_api.reply_message(event.reply_token, msgs)
		else:
			line_bot_api.reply_message(event.reply_token, [
				TextSendMessage(text="尚未驗證，請點選主選單的『開始驗證』。")
			])
