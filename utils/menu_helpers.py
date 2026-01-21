# -*- coding: utf-8 -*-
from linebot.models import TextSendMessage, FlexSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS  # 管理員清單
from secrets import choice as secrets_choice

# ================= 馬年主題配色 =================
HORSE_BG_1   = "#8B4513"  # 棕褐色（馬鞍褐）
HORSE_BG_2   = "#654321"  # 深褐色（深咖啡）
HORSE_GOLD   = "#FFD700"  # 金色（金馬獎）
HORSE_CREAM  = "#FFF8DC"  # 奶油色
HORSE_RED    = "#DC143C"  # 中國紅（吉祥紅）
HORSE_GREEN  = "#228B22"  # 草原綠
HORSE_ACCENT = "#CD853F"  # 秋麥色
HORSE_PURPLE = "#8B008B"  # 深紫（高貴紫）
HORSE_BORDER = "#A0522D"  # 赭褐分隔線

# 馬年主選單專用配色
HORSE_MENU_BG_1   = "#4A2C2A"  # 深栗色
HORSE_MENU_BG_2   = "#3B1E1C"  # 更深栗
HORSE_MENU_GOLD   = "#F4A460"  # 沙棕金
HORSE_MENU_LIGHT  = "#F5DEB3"  # 小麥色
HORSE_MENU_BLUE   = "#8B7355"  # 咖啡藍
HORSE_MENU_ACCENT = "#D2691E"  # 巧克力色
HORSE_MENU_PURPLE = "#8B4789"  # 蘭花紫

# ====== 共用：隨機客服/預約群連結 ======
def choose_link():
    group = [
        "https://line.me/ti/p/g7TPO_lhAL",
        "https://line.me/ti/p/emkjaMQkMK",
        "https://line.me/ti/p/AKRUvSCLRC",
    ]
    return secrets_choice(group)

# ====== JKF 廣告連結（可獨立修改）======
JKF_LINKS = [
    {"label": "茗殿 - 主頁推薦",     "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"},
    {"label": "泰式料理菜單 - 1",   "url": "https://www.jkforum.net/p/thread-16422277-1-1.html"},
    {"label": "泰式料理菜單 - 2",   "url": "https://www.jkforum.net/p/thread-17781450-1-1.html"},
    {"label": "越式料理小吃 - 1",   "url": "https://www.jkforum.net/thread-18976516-1-1.html"},
    {"label": "越式料理小吃 - 2",   "url": "https://www.jkforum.net/p/thread-17742482-1-1.html"},
    {"label": "檔期推薦 - 多多",     "url": "https://www.jkforum.net/p/thread-20296958-1-1.html"},
    {"label": "檔期推薦 - 莎莎",     "url": "https://www.jkforum.net/p/thread-20296970-1-1.html"},
    {"label": "檔期推薦 - 心心",     "url": "https://www.jkforum.net/p/thread-10248540-1-1.html"},
    {"label": "本期空缺中",         "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"},
    {"label": "本期空缺中",         "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"},
]

# ====== 廣告專區（馬年主題）======
def get_ad_menu():
    btn_primary   = HORSE_RED
    btn_secondary = HORSE_ACCENT

    buttons = []
    for i, link in enumerate(JKF_LINKS):
        buttons.append({
            "type": "button",
            "action": {"type": "uri", "label": link["label"], "uri": link["url"]},
            "style": "primary",
            "color": btn_primary if i % 2 == 0 else btn_secondary
        })

    buttons.append({
        "type": "button",
        "action": {"type": "message", "label": "🏛️ 回主選單", "text": "主選單"},
        "style": "primary",
        "color": btn_secondary
    })

    return FlexSendMessage(
        alt_text="廣告專區",
        contents={
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": HORSE_BG_2,
                "paddingAll": "16px",
                "contents": [{
                    "type": "text",
                    "text": "🐴 茗殿廣告資訊站",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": HORSE_GOLD
                }]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": HORSE_BG_2,
                "spacing": "md",
                "contents": [
                    {"type": "separator", "color": HORSE_BORDER},
                    {"type": "box", "layout": "vertical", "spacing": "sm", "margin": "lg", "contents": buttons}
                ]
            },
            "styles": {"body": {"separator": False}}
        }
    )

# ====== 馬年主選單（兩頁 Carousel） ======
def get_menu_carousel():
    # 馬年主選單配色
    COLOR_PRIMARY = HORSE_MENU_BLUE
    COLOR_ACCENT = HORSE_MENU_ACCENT
    COLOR_SECONDARY = HORSE_MENU_GOLD
    COLOR_GRAY = HORSE_MENU_LIGHT
    COLOR_ALERT = HORSE_MENU_PURPLE

    page1 = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": HORSE_MENU_BG_1,
            "paddingAll": "16px",
            "contents": [{
                "type": "text",
                "text": "🐴 馬年吉祥選單 1/2",
                "weight": "bold",
                "align": "center",
                "size": "lg",
                "color": HORSE_MENU_GOLD
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": HORSE_MENU_BG_1,
            "spacing": "md",
            "contents": [
                {"type": "separator", "color": HORSE_MENU_BLUE},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {"type": "button", "action": {"type": "message", "label": "🔑 我的驗證", "text": "驗證資訊"}, "style": "primary", "color": COLOR_PRIMARY},
                        {"type": "button", "action": {"type": "message", "label": "🎁 每日抽獎", "text": "每日抽獎"}, "style": "primary", "color": COLOR_ACCENT},
                        {"type": "button", "action": {"type": "message", "label": "📢 廣告專區", "text": "廣告專區"}, "style": "primary", "color": COLOR_SECONDARY},
                        {"type": "button", "action": {"type": "uri", "label": "🗓️ 班表查詢", "uri": "https://t.me/+svlFjBpb4hxkYjFl"}, "style": "secondary", "color": COLOR_GRAY},
                        {"type": "button", "action": {"type": "uri", "label": "📲 預約諮詢", "uri": choose_link()}, "style": "secondary", "color": COLOR_ALERT}
                    ]
                }
            ]
        }
    }

    page2 = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": HORSE_MENU_BG_2,
            "paddingAll": "16px",
            "contents": [{
                "type": "text",
                "text": "🐴 馬年吉祥選單 2/2",
                "weight": "bold",
                "align": "center",
                "size": "lg",
                "color": HORSE_MENU_GOLD
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": HORSE_MENU_BG_2,
            "spacing": "md",
            "contents": [
                {"type": "separator", "color": HORSE_MENU_BLUE},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {"type": "button", "action": {"type": "uri", "label": "💬 聊天社群", "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"}, "style": "primary", "color": COLOR_ACCENT},
                        {"type": "button", "action": {"type": "message", "label": "💸 優惠券專區", "text": "折價券管理"}, "style": "primary", "color": COLOR_PRIMARY},
                        {"type": "button", "action": {"type": "message", "label": "💳 儲值金專區", "text": "儲值金"}, "style": "primary", "color": COLOR_ACCENT},
                        {"type": "button", "action": {"type": "message", "label": "☎️ 服務專線", "text": "📞 茗殿熱線：0987-346-208\n歡迎來電洽詢，專人即時服務！"}, "style": "primary", "color": COLOR_ALERT},
                        {"type": "button", "action": {"type": "message", "label": "🌟 最新活動", "text": "活動快訊"}, "style": "primary", "color": COLOR_SECONDARY}
                    ]
                }
            ]
        }
    }

    return FlexSendMessage(
        alt_text="馬年吉祥選單",
        contents={"type": "carousel", "contents": [page1, page2]}
    )

# ====== 封裝回覆 =======
def reply_with_menu(reply_token, text=None):
    msgs = []
    if text:
        msgs.append(TextSendMessage(text=text))
    msgs.append(get_menu_carousel())
    line_bot_api.reply_message(reply_token, msgs)

def reply_with_ad_menu(reply_token):
    line_bot_api.reply_message(reply_token, [get_ad_menu()])

# ====== 呼叫管理員推播 =======
def notify_admins(user_id, display_name=None):
    from models import Whitelist
    user = Whitelist.query.filter_by(line_user_id=user_id).first()

    if user:
        code = user.id or "未登記"
        name = user.name or (display_name or "未登記")
        line_id = user.line_id or "未登記"
    else:
        code = "未登記"
        name = display_name or "未登記"
        line_id = "未登記"

    msg = (
        "【用戶呼叫管理員】\n"
        f"暱稱：{name}\n"
        f"用戶編號：{code}\n"
        f"LINE ID：{line_id}\n"
        f"訊息：呼叫管理員\n\n"
        f"➡️ 若要私訊此用戶，請輸入：/msg {user_id} 你的回覆內容"
    )

    for admin_id in ADMIN_IDS:
        try:
            line_bot_api.push_message(admin_id, TextSendMessage(text=msg))
        except Exception as e:
            print(f"通知管理員失敗：{admin_id}，錯誤：{e}")