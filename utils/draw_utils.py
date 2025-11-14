import random
from datetime import datetime, time
from pytz import timezone
from linebot.models import FlexSendMessage
from models import Whitelist, StoredValueWallet, StoredValueCoupon
from typing import Optional

def draw_coupon():
    """
    執行抽獎，根據機率回傳金額
    """
    chance = random.random()
    if chance < 0.7:
        return 0  # 未中獎 70%
    else:
        prize_chance = (chance - 0.7) / 0.3  # 0~1之間
        if prize_chance < 0.01:
            return 500  # 1%
        elif prize_chance < 0.03:
            return 300  # 2%
        elif prize_chance < 0.08:
            return 200  # 5%
        else:
            return 100  # 95%

def has_drawn_today(user_id, CouponModel):
    """
    檢查今天是否已抽過獎（今日有任何一筆就算抽過，不分 type）
    """
    tz = timezone("Asia/Taipei")
    today = datetime.now(tz).date()
    return CouponModel.query.filter_by(line_user_id=user_id, date=str(today)).first()

def save_coupon_record(user_id, amount, CouponModel, db, type: str = "draw", coupon_type: Optional[str] = None):
    """
    儲存今日抽獎結果（Coupon 表），若中獎(amount>0) 同步建立 StoredValueCoupon（當日到期，source=draw）。
    """
    tz = timezone("Asia/Taipei")
    now = datetime.now(tz)
    today = now.date()
    # 1) 紀錄於 Coupon (歷史)
    record_type = coupon_type if coupon_type else type
    new_coupon = CouponModel(
        line_user_id=user_id,
        amount=amount,
        date=str(today),
        created_at=now,
        type=record_type
    )
    db.session.add(new_coupon)
    # 2) 若中獎，寫入 stored_value_coupon 以便錢包/扣款使用
    try:
        if amount and amount > 0:
            wl = Whitelist.query.filter_by(line_user_id=user_id).first()
            if wl:
                wallet = StoredValueWallet.query.filter_by(whitelist_id=wl.id).first()
                if not wallet:
                    wallet = StoredValueWallet()
                    wallet.whitelist_id = wl.id
                    wallet.phone = wl.phone
                    wallet.balance = 0
                    db.session.add(wallet)
                    db.session.flush()
                # 設定到期為當日 23:59:59
                expiry_dt = datetime.combine(today, time(23,59,59))
                # 儲存為台北時間 aware datetime，避免誤判日期
                try:
                    expiry_dt = timezone('Asia/Taipei').localize(expiry_dt)
                except Exception:
                    pass
                svc = StoredValueCoupon()
                svc.wallet_id = wallet.id
                svc.amount = amount
                svc.expiry_date = expiry_dt
                svc.source = 'draw'
                db.session.add(svc)
    except Exception:
        # 若寫入 stored_value_coupon 失敗，不阻斷 Coupon 記錄
        pass
    db.session.commit()
    return new_coupon

def get_today_coupon_flex(user_id, display_name, amount):
    """
    回傳當日抽獎 FlexMessage
    """
    now = datetime.now(timezone("Asia/Taipei"))
    today_str = now.strftime("%Y/%m/%d")
    emoji_date = f"📅 {now.strftime('%m/%d')}"
    expire_time = "23:59"

    if amount == 0:
        text = "很可惜沒中獎呢～明天再試試看吧🌙"
        color = "#999999"
    else:
        text = f"🎁 恭喜你抽中 {amount} 元折價券"
        color = "#FF9900"

    return FlexSendMessage(
        alt_text="每日抽獎結果",
        contents={
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": emoji_date,
                        "weight": "bold",
                        "size": "lg"
                    },
                    {
                        "type": "text",
                        "text": f"用戶：{display_name}",
                        "size": "sm",
                        "color": "#888888"
                    },
                    {
                        "type": "text",
                        "text": f"日期：{today_str}",
                        "size": "sm",
                        "color": "#888888"
                    },
                    {"type": "separator"},
                    {
                        "type": "text",
                        "text": text,
                        "size": "xl",
                        "weight": "bold",
                        "color": color,
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": f"🕒 有效至：今日 {expire_time}",
                        "size": "sm",
                        "color": "#999999",
                        "align": "center"
                    }
                ]
            }
        }
    )
