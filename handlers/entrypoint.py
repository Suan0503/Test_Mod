"""
LINE Bot 入口事件處理 (entrypoint)
- 負責分流各種訊息事件到對應 handler
"""
from linebot.models import MessageEvent, TextMessage, ImageMessage, FollowEvent, TextSendMessage
from extensions import handler, line_bot_api, db
from utils.menu_helpers import reply_with_menu, notify_admins, reply_with_ad_menu
from handlers.report import handle_report
from handlers.admin import handle_admin
from utils.temp_users import temp_users
from models.whitelist import Whitelist
from models.coupon import Coupon
from utils.draw_utils import draw_coupon, has_drawn_today, save_coupon_record, get_today_coupon_flex
import pytz
from datetime import datetime
from handlers.follow import handle_follow
from handlers.image import handle_image
import logging
logging.basicConfig(level=logging.INFO)

@handler.add(FollowEvent)
def on_follow(event):
    logging.info(f"[FollowEvent] Source: {event.source}")
    handle_follow(event, line_bot_api)

@handler.add(MessageEvent, message=ImageMessage)
def on_image(event):
    logging.info(f"[ImageMessage] user_id={event.source.user_id}")
    handle_image(event)

@handler.add(MessageEvent, message=TextMessage)
def entrypoint(event):
    user_text = event.message.text.strip()
    user_id = event.source.user_id
    logging.info(f"[TextMessage] user_id={user_id} text={user_text}")
    if user_text == "廣告專區":
        reply_with_ad_menu(event.reply_token)
        return
    if user_id in temp_users and (
        temp_users[user_id].get("report_pending") or
        temp_users[user_id].get("report_ng_pending")
    ):
        handle_report(event)
        return
    if user_text in ["回報文", "Report", "report"]:
        handle_report(event)
        return
    if user_text.startswith("/msg "):
        handle_admin(event)
        return
    if user_text == "驗證資訊":
        tz = pytz.timezone("Asia/Taipei")
        user = Whitelist.query.filter_by(line_user_id=user_id).first()
        if user:
            reply = (
                f"📱 {user.phone}\n"
                f"🌸 暱稱：{user.name or '未登記'}\n"
                f"       個人編號：{user.id}\n"
                f"🔗 LINE ID：{user.line_id or '未登記'}\n"
                f"🕒 {user.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"✅ 驗證成功，歡迎加入茗殿\n"
                f"🌟 加入密碼：ming666"
            )
        else:
            reply = "查無你的驗證資訊，請先完成驗證流程。"
        reply_with_menu(event.reply_token, reply)
        return
    if user_text in ["每日抽獎"]:
        profile = None
        display_name = "用戶"
        try:
            profile = line_bot_api.get_profile(user_id)
            display_name = profile.display_name
        except Exception:
            pass
        today_coupon = has_drawn_today(user_id, Coupon)
        if today_coupon:
            amount = today_coupon.amount
            flex_msg = get_today_coupon_flex(user_id, display_name, amount)
            line_bot_api.reply_message(event.reply_token, [flex_msg])
            return
        else:
            amount = draw_coupon()
            save_coupon_record(user_id, amount, Coupon, db)
            flex_msg = get_today_coupon_flex(user_id, display_name, amount)
            line_bot_api.reply_message(event.reply_token, [flex_msg])
            return
