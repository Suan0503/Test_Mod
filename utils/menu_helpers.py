
from linebot.models import TextSendMessage, FlexSendMessage
from datetime import datetime
import pytz

def get_menu_carousel():
    # 依照原專案內容，回傳主選單 carousel
    return {
        "type": "template",
        "altText": "主選單",
        "template": {
            "type": "buttons",
            "title": "主選單",
            "text": "請選擇功能",
            "actions": [
                {"type": "message", "label": "驗證資訊", "text": "驗證資訊"},
                {"type": "message", "label": "每日抽獎", "text": "每日抽獎"},
                {"type": "message", "label": "券紀錄", "text": "券紀錄"}
            ]
        }
    }

def get_verification_info(member, display_name):
    tz = pytz.timezone("Asia/Taipei")
    if member:
        reply = (
            f"📱 {member.phone}\n"
            f"🌸 暱稱：{member.name or display_name}\n"
            f"       個人編號：{member.id}\n"
            f"🔗 LINE ID：{member.line_id or '未登記'}\n"
            f"🕒 {member.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
            f"✅ 驗證成功，歡迎加入茗殿\n"
            f"🌟 加入密碼：ming666"
        )
        return [TextSendMessage(text=reply), get_menu_carousel()]
    else:
        return [TextSendMessage(text="⚠️ 你尚未完成驗證，請輸入手機號碼進行驗證。")]

def get_today_coupon_flex(display_name, amount):
    now = datetime.now(pytz.timezone("Asia/Taipei"))
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
                    {"type": "text", "text": emoji_date, "weight": "bold", "size": "lg"},
                    {"type": "text", "text": f"用戶：{display_name}", "size": "sm", "color": "#888888"},
                    {"type": "text", "text": f"日期：{today_str}", "size": "sm", "color": "#888888"},
                    {"type": "separator"},
                    {"type": "text", "text": text, "size": "xl", "weight": "bold", "color": color, "align": "center", "margin": "md"},
                    {"type": "text", "text": f"🕒 有效至：今日 {expire_time}", "size": "sm", "color": "#999999", "align": "center"}
                ]
            }
        }
    )

def get_coupon_record_message(draw_today, report_month):
    msg = "🎁【今日抽獎券】\n"
    if draw_today:
        for c in draw_today:
            msg += f"　　• 日期：{c.date}｜金額：{c.amount}元\n"
    else:
        msg += "　　無紀錄\n"
    msg += "\n📝【本月回報文抽獎券】\n"
    if report_month:
        for c in report_month:
            no = getattr(c, 'report_no', '') or ""
            if getattr(c, 'amount', 0) > 0:
                msg += f"　　• 日期：{c.date}｜編號：{no}｜金額：{c.amount}元\n"
            else:
                msg += f"　　• 日期：{c.date}｜編號：{no}\n"
    else:
        msg += "　　無紀錄\n"
    msg += "\n※ 回報文抽獎券中獎名單與金額，將於每月抽獎公布"
    return TextSendMessage(text=msg)
