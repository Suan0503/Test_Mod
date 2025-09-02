
import random
from datetime import datetime, date
from pytz import timezone
from linebot.models import FlexSendMessage
from typing import Optional, Dict, Any, Tuple, List

# ────────────── 常量與設定 ──────────────
COUPON_PRIZES: List[Tuple[float, int]] = [
    (0.000001, 500),
    (0.003, 300),
    (0.07, 200),
    (0.22, 100),
    (1.0, 0),  # 其他機率
]
COUPON_TEXTS = {
    0: ("很可惜沒中獎呢～明天再試試看吧🌙", "#999999"),
    "default": ("🎁 恭喜你抽中 {amount} 元折價券", "#FF9900"),
}
FLEX_TEMPLATE = {
    "alt_text": "每日抽獎結果",
    "user_label": "用戶：",
    "date_label": "日期：",
    "expire_label": "🕒 有效至：今日 {expire_time}",
    "expire_time": "23:59",
}

# ────────────── 工具函式 ──────────────
def get_today(tz_str: str = "Asia/Taipei") -> date:
    tz = timezone(tz_str)
    return datetime.now(tz).date()

def get_now(tz_str: str = "Asia/Taipei") -> datetime:
    tz = timezone(tz_str)
    return datetime.now(tz)

def draw_coupon() -> Dict[str, Any]:
    """
    執行抽獎，根據機率回傳獎品 dict
    {"amount": int, "type": str}
    """
    chance = random.random()
    for prob, amount in COUPON_PRIZES:
        if chance < prob:
            return {"amount": amount, "type": "cash"}
    return {"amount": 0, "type": "none"}

def has_drawn_today(user_id: str, CouponModel) -> Optional[Any]:
    """
    檢查今天是否已抽過獎（今日有任何一筆就算抽過，不分 type）
    """
    today = get_today()
    return CouponModel.query.filter_by(line_user_id=user_id, date=str(today)).first()

def save_coupon_record(user_id: str, amount: int, CouponModel, db) -> Optional[Any]:
    """
    儲存今日抽獎結果，失敗回傳 None
    """
    today = get_today()
    try:
        new_coupon = CouponModel(
            line_user_id=user_id,
            amount=amount,
            date=str(today),
            created_at=get_now()
        )
        db.session.add(new_coupon)
        db.session.commit()
        return new_coupon
    except Exception as e:
        # 可加 log 或回報
        return None

def get_today_coupon_flex(user_id: str, display_name: str, amount: int) -> FlexSendMessage:
    """
    回傳當日抽獎 FlexMessage，模板化，易於維護與擴充
    """
    now = get_now()
    today_str = now.strftime("%Y/%m/%d")
    emoji_date = f"📅 {now.strftime('%m/%d')}"
    expire_time = FLEX_TEMPLATE["expire_time"]
    if amount == 0:
        text, color = COUPON_TEXTS[0]
    else:
        _, color = COUPON_TEXTS["default"]
        text = f"🎁 恭喜你抽中 {amount} 元折價券"
    return FlexSendMessage(
        alt_text=FLEX_TEMPLATE["alt_text"],
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
                        "text": f"{FLEX_TEMPLATE['user_label']}{display_name}",
                        "size": "sm",
                        "color": "#888888"
                    },
                    {
                        "type": "text",
                        "text": f"{FLEX_TEMPLATE['date_label']}{today_str}",
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
                        "text": FLEX_TEMPLATE["expire_label"].format(expire_time=expire_time),
                        "size": "sm",
                        "color": "#999999",
                        "align": "center"
                    }
                ]
            }
        }
    )
