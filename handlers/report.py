"""
回報事件處理 (handle_report)
- 處理用戶回報文流程、回報抽獎券
"""
from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent, TextSendMessage
)
from extensions import line_bot_api, db
from models.whitelist import Whitelist
from models.coupon import Coupon
from utils.temp_users import temp_users
from storage import ADMIN_IDS
import re, time, logging
from datetime import datetime
import pytz
logger = logging.getLogger(__name__)
report_pending_map = {}

def handle_report(event):
    user_id = getattr(event.source, "user_id", None)
    user_text = (getattr(event.message, "text", "") or "").strip()
    tz = pytz.timezone("Asia/Taipei")
    try:
        profile = line_bot_api.get_profile(user_id) if user_id else None
        display_name = profile.display_name if profile else "用戶"
    except Exception:
        display_name = "用戶"
    if user_text in ["回報文", "Report", "report"]:
        temp_users[user_id] = {"report_pending": True}
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入要回報的網址（請直接貼網址）：\n\n如需取消，請輸入「取消」")
        )
        return
    if user_id in temp_users and temp_users[user_id].get("report_pending"):
        if user_text == "取消":
            temp_users.pop(user_id, None)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="已取消回報流程，回到主選單！")
            )
            return
        url = user_text
        if not re.match(r"^https?://", url):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入正確的網址格式（必須以 http:// 或 https:// 開頭）\n如需取消，請輸入「取消」")
            )
            return
        wl = Whitelist.query.filter_by(line_user_id=user_id).first() if user_id else None
        user_number = wl.id if wl else ""
        user_lineid = wl.line_id if wl else ""
        try:
            last_coupon = Coupon.query.filter(Coupon.report_no != None).order_by(Coupon.id.desc()).first()
        except Exception:
            logger.exception("查詢最後一筆 coupon 時發生錯誤")
            last_coupon = None
        if last_coupon and getattr(last_coupon, "report_no", None) and str(last_coupon.report_no).isdigit():
            report_no = int(last_coupon.report_no) + 1
        else:
            report_no = 1
        report_no_str = f"{report_no:03d}"
        short_text = f"網址：{url}" if len(url) < 55 else "新回報文，請點選按鈕處理"
        detail_text = (
            f"【用戶回報文】編號-{report_no_str}\n"
            f"暱稱：{display_name}\n"
            f"用戶編號：{user_number}\n"
            f"LINE ID：{user_lineid}\n"
            f"網址：{url}"
        )
        report_id = f"{user_id}_{int(time.time()*1000)}"
        report_info = {
            "user_id": user_id,
            "display_name": display_name,
            "user_number": user_number,
            "user_lineid": user_lineid,
            "url": url,
            "report_no": report_no_str,
            "admins": list(ADMIN_IDS),
            "created_at": datetime.now(tz),
        }
        report_pending_map[report_id] = report_info
