import random
from datetime import datetime
from pytz import timezone

def draw_coupon():
    chance = random.random()
    if chance < 0.02:
        return 300
    elif chance < 0.06:
        return 200
    elif chance < 0.40:
        return 100
    else:
        return 0

def has_drawn_today(user_id, CouponModel):
    tz = timezone("Asia/Taipei")
    today = datetime.now(tz).date()
    return CouponModel.query.filter_by(line_user_id=user_id, date=str(today)).first()

def save_coupon_record(user_id, amount, CouponModel, db):
    tz = timezone("Asia/Taipei")
    today = datetime.now(tz).date()
    new_coupon = CouponModel(
        line_user_id=user_id,
        amount=amount,
        date=str(today),
        created_at=datetime.now(tz)
    )
    db.session.add(new_coupon)
    db.session.commit()
    return new_coupon

def get_today_coupon_flex(user_id, display_name, amount):
    # 依照你原本的專案補上 Flex 物件產生邏輯
    from linebot.models import FlexSendMessage
    # 這裡只放 placeholder（請依你原邏輯補上）
    return FlexSendMessage(
        alt_text="今日抽獎結果",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"{display_name} 今日抽獎金額：{amount}", "size": "lg"}
                ]
            }
        }
    )