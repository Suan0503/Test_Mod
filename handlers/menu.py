

from linebot.models import MessageEvent, TextMessage, TextSendMessage
from utils.menu_helpers import get_menu_carousel, get_verification_info, get_today_coupon_flex, get_coupon_record_message
from utils.temp_users import get_temp_user
from models.verify_user import Member
from sqlalchemy.orm import sessionmaker
from flask import current_app
import pytz
from datetime import datetime

def register_menu_handler(handler):
    @handler.add(MessageEvent, message=TextMessage)
    def handle_menu(event):
        user_id = event.source.user_id
        user_text = event.message.text.strip()
        temp = get_temp_user(user_id)
        SessionLocal = sessionmaker(bind=current_app.engine)
        session = SessionLocal()
        tz = pytz.timezone("Asia/Taipei")
        display_name = "用戶"
        # 主選單
        if user_text in ["主選單", "功能選單", "選單", "menu", "Menu"]:
            if event.reply_token:
                handler.bot.reply_message(event.reply_token, get_menu_carousel())
            return
        # 驗證資訊
        if user_text == "驗證資訊":
            member = session.query(Member).filter_by(line_user_id=user_id).first()
            msgs = get_verification_info(member, display_name)
            if event.reply_token:
                for msg in msgs:
                    handler.bot.reply_message(event.reply_token, msg)
            return
        # 每日抽獎
        if user_text == "每日抽獎":
            member = session.query(Member).filter_by(line_user_id=user_id).first()
            if not member:
                if event.reply_token:
                    handler.bot.reply_message(event.reply_token, TextSendMessage(text="⚠️ 你尚未完成驗證，請先完成驗證才能參加每日抽獎！"))
                return
            today_str = datetime.now(tz).strftime("%Y-%m-%d")
            # Coupon 資料表需自行補充
            coupon = None
            if coupon:
                flex = get_today_coupon_flex(display_name, coupon.amount)
                if event.reply_token:
                    handler.bot.reply_message(event.reply_token, flex)
                return
            amount = 0  # 這裡可呼叫抽獎邏輯
            flex = get_today_coupon_flex(display_name, amount)
            if event.reply_token:
                handler.bot.reply_message(event.reply_token, flex)
            return
        # 券紀錄
        if user_text in ["券紀錄", "我的券紀錄"]:
            # Coupon 資料表需自行補充
            draw_today = []
            report_month = []
            msg = get_coupon_record_message(draw_today, report_month)
            if event.reply_token:
                handler.bot.reply_message(event.reply_token, msg)
            return
