

from linebot.models import MessageEvent, TextMessage, TextSendMessage
from utils.menu_helpers import get_menu_carousel, get_verification_info, get_today_coupon_flex, get_coupon_record_message
from utils.temp_users import get_temp_user
from models.verify_user import Member
from models.coupon import Coupon
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
    # 使用 SQLAlchemy session，假設 app.py 已有 engine
    engine = current_app.config.get('ENGINE')
    SessionLocal = sessionmaker(bind=engine)
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
            coupon = session.query(Coupon).filter_by(line_user_id=user_id, date=today_str, type="draw").first()
            if coupon:
                flex = get_today_coupon_flex(display_name, coupon.amount)
                if event.reply_token:
                    handler.bot.reply_message(event.reply_token, flex)
                return
            # 執行抽獎
            import random
            chance = random.random()
            if chance < 0.000001:
                amount = 500
            elif chance < 0.003:
                amount = 300
            elif chance < 0.07:
                amount = 200
            elif chance < 0.42:
                amount = 100
            else:
                amount = 0
            new_coupon = Coupon(
                line_user_id=user_id,
                amount=amount,
                date=today_str,
                type="draw",
                created_at=datetime.now(tz)
            )
            session.add(new_coupon)
            session.commit()
            flex = get_today_coupon_flex(display_name, amount)
            if event.reply_token:
                handler.bot.reply_message(event.reply_token, flex)
            return
        # 券紀錄
        if user_text in ["券紀錄", "我的券紀錄"]:
            today = datetime.now(tz).date()
            month_str = today.strftime("%Y-%m")
            user_coupons = session.query(Coupon).filter_by(line_user_id=user_id).all()
            draw_today = [c for c in user_coupons if c.type == "draw" and c.date == str(today)]
            report_month = [c for c in user_coupons if c.type == "report" and c.date.startswith(month_str)]
            msg = get_coupon_record_message(draw_today, report_month)
            if event.reply_token:
                handler.bot.reply_message(event.reply_token, msg)
            return
