# -*- coding: utf-8 -*-
from linebot.models import TextSendMessage, FlexSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS  # 管理員清單
from secrets import choice as secrets_choice

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
    {"label": "越式料理小吃 - 1",   "url": "https://www.jkforum.net/p/thread-18976516-1-1.html"},
    {"label": "越式料理小吃 - 2",   "url": "https://www.jkforum.net/p/thread-17742482-1-1.html"},
    {"label": "檔期推薦 - 多多",     "url": "https://www.jkforum.net/p/thread-20296958-1-1.html"},
    {"label": "檔期推薦 - 莎莎",     "url": "https://www.jkforum.net/p/thread-20296970-1-1.html"},
    {"label": "檔期推薦 - 心心",     "url": "https://www.jkforum.net/p/thread-10248540-1-1.html"},
    {"label": "本期空缺中",         "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"},
    {"label": "本期空缺中",         "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"},
]

# ====== 廣告專區（深夜藍主題，白字）======
def get_ad_menu():
    btn_primary = "#2C4A6B"   # 深藍
    btn_secondary = "#4B99C2" # 天藍

    buttons = []
    for i, link in enumerate(JKF_LINKS):
        buttons.append({
            "type": "button",
            "action": {"type": "uri", "label": link["label"], "uri": link["url"]},
            "style": "primary",
            "color": btn_primary if i % 2 == 0 else btn_secondary
        })

    # 回主選單
    buttons.append({
        "type": "button",
        "action": {"type": "message", "label": "🏠 回主選單", "text": "主選單"},
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
                "backgroundColor": "#1C2636",
                "paddingAll": "16px",
                "contents": [{
                    "type": "text",
                    "text": "🏖️ 夏日廣告專區",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": "#FFD700"
                }]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#1C2636",
                "spacing": "md",
                "contents": [
                    {"type": "separator", "color": "#31485C"},
                    {"type": "box", "layout": "vertical", "spacing": "sm", "margin": "lg", "contents": buttons}
                ]
            },
            "styles": {"body": {"separator": False}}
        }
    )

# ====== 開學祭主選單（兩頁 Carousel）======
def get_menu_carousel():
    # 校園配色：櫻花粉 / 粉紫，按鈕色採文具色系
    main_bg1   = "#FFE4EC"  # 櫻花粉
    main_bg2   = "#F8D9FF"  # 粉紫
    pen_pink   = "#F06292"  # 粉紅筆
    pen_yellow = "#FFD54F"  # 黃便條
    pen_green  = "#81C784"  # 綠筆
    pen_blue   = "#64B5F6"  # 藍筆
    pen_orange = "#FF8A65"  # 橘筆
    pen_ltblue = "#4FC3F7"  # 淺藍
    pen_ltgrn  = "#AED581"  # 淺綠
    pen_gray   = "#B39DDB"  # 灰紫

    # ---------- 第一頁 ----------
    page1 = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": main_bg1,
            "paddingAll": "16px",
            "contents": [{
                "type": "text",
                "text": "🌸 櫻花開學祭選單 1/2",
                "weight": "bold",
                "align": "center",
                "size": "lg",
                "color": "#C2185B"
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": main_bg1,
            "spacing": "md",
            "contents": [
                {"type": "separator", "color": pen_gray},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🎒 開啟主選單", "text": "驗證資訊"},
                            "style": "primary",
                            "color": pen_pink
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🎁 開學抽獎", "text": "每日抽獎"},
                            "style": "primary",
                            "color": pen_yellow
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "📢 活動專區", "text": "廣告專區"},
                            "style": "primary",
                            "color": pen_green
                        },
                        {
                            "type": "button",
                            "action": {"type": "uri", "label": "📅 班表查詢", "uri": "https://t.me/+svlFjBpb4hxkYjFl"},
                            "style": "secondary",
                            "color": "#FFFFFF"
                        },
                        {
                            "type": "button",
                            "action": {"type": "uri", "label": "🕶️ 預約諮詢", "uri": choose_link()},
                            "style": "secondary",
                            "color": pen_orange
                        }
                    ]
                }
            ]
        }
    }

    # ---------- 第二頁 ----------
    page2 = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": main_bg2,
            "paddingAll": "16px",
            "contents": [{
                "type": "text",
                "text": "🏫 茗殿開學祭選單 2/2",
                "weight": "bold",
                "align": "center",
                "size": "lg",
                "color": "#7B1FA2"
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": main_bg2,
            "spacing": "md",
            "contents": [
                {"type": "separator", "color": pen_gray},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "🌺 茗殿討論區",
                                "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
                            },
                            "style": "primary",
                            "color": pen_ltgrn
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "📝 回報文登記（暫停）", "text": "回報文"},
                            "style": "primary",
                            "color": pen_pink
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "💸 折價券管理", "text": "折價券管理"},
                            "style": "primary",
                            "color": pen_ltblue
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🧊 呼叫管理員（暫停）", "text": "呼叫管理員"},
                            "style": "secondary",
                            "color": pen_gray
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🌞 活動快訊（暫停）", "text": "活動快訊"},
                            "style": "primary",
                            "color": pen_orange
                        }
                    ]
                }
            ]
        }
    }

    return FlexSendMessage(
        alt_text="開學祭主功能選單",
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
    # 避免硬性相依：在使用時才 import
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