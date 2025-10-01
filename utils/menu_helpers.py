# -*- coding: utf-8 -*-
from linebot.models import TextSendMessage, FlexSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS  # 管理員清單
from secrets import choice as secrets_choice



# ================= 萬聖節配色 =================
# 主題：南瓜橘、幽靈白、紫夜、糖果粉、蝙蝠黑
HAL_BG_1   = "#2D1436"  # 紫夜（頁1底）
HAL_BG_2   = "#1B0B1F"  # 深紫黑（頁2底）
HAL_ORANGE = "#FF7518"  # 南瓜橘
HAL_WHITE  = "#F8F8F8"  # 幽靈白
HAL_PINK   = "#FFB6B9"  # 糖果粉
HAL_BLACK  = "#231F20"  # 蝙蝠黑
HAL_PURPLE = "#7C3AED"  # 萬聖紫



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

# ====== 廣告專區（魔法學院主題）======
def get_ad_menu():
    btn_primary   = HAL_ORANGE   # 南瓜橘
    btn_secondary = HAL_PURPLE   # 萬聖紫

    buttons = []
    for i, link in enumerate(JKF_LINKS):
        buttons.append({
            "type": "button",
            "action": {"type": "uri", "label": link["label"], "uri": link["url"]},
            "style": "primary",  # 白字
            "color": btn_primary if i % 2 == 0 else btn_secondary
        })

    # 回主選單
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
                "backgroundColor": HAL_BG_2,
                "paddingAll": "16px",
                "contents": [{
                    "type": "text",
                    "text": "🦇 萬聖廣告專區",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": HAL_ORANGE
                }]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": HAL_BG_2,
                "spacing": "md",
                "contents": [
                    {"type": "separator", "color": HAL_BLACK},
                    {"type": "box", "layout": "vertical", "spacing": "sm", "margin": "lg", "contents": buttons}
                ]
            },
            "styles": {"body": {"separator": False}}
        }
    )

# ====== 魔法學院主選單（兩頁 Carousel）======
def get_menu_carousel():

    # 第一頁 - 中秋主題
    page1 = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": HAL_BG_1,
            "paddingAll": "16px",
            "contents": [{
                "type": "text",
                "text": "� 萬聖節驚魂選單 1/2",
                "weight": "bold",
                "align": "center",
                "size": "lg",
                "color": HAL_ORANGE
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": HAL_BG_1,
            "spacing": "md",
            "contents": [
                {"type": "separator", "color": HAL_BLACK},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "� 幽靈身分證（個人資訊）", "text": "驗證資訊"},
                            "style": "primary",
                            "color": HAL_WHITE
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🎃 南瓜抽獎", "text": "每日抽獎"},
                            "style": "primary",
                            "color": HAL_ORANGE
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🕸️ 驚魂大平台(廣告)", "text": "廣告專區"},
                            "style": "primary",
                            "color": HAL_PURPLE
                        },
                        {
                            "type": "button",
                            "action": {"type": "uri", "label": "� 糖果賣場(班表群)", "uri": "https://t.me/+svlFjBpb4hxkYjFl"},
                            "style": "secondary",
                            "color": HAL_PINK
                        },
                        {
                            "type": "button",
                            "action": {"type": "uri", "label": "🦇 專屬引導員", "uri": choose_link()},
                            "style": "secondary",
                            "color": HAL_BLACK
                        }
                    ]
                }
            ]
        }
    }


    # 第二頁 - 中秋主題
    page2 = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": HAL_BG_2,
            "paddingAll": "16px",
            "contents": [{
                "type": "text",
                "text": "🦇 萬聖節驚魂選單 2/2",
                "weight": "bold",
                "align": "center",
                "size": "lg",
                "color": HAL_ORANGE
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": HAL_BG_2,
            "spacing": "md",
            "contents": [
                {"type": "separator", "color": HAL_BLACK},
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
                                "label": "� 南瓜大廳(社群)",
                                "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
                            },
                            "style": "primary",
                            "color": HAL_ORANGE
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "📝 萬聖投稿（暫停）", "text": "回報文"},
                            "style": "primary",
                            "color": HAL_PINK
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "� 糖果兌換袋(折價券)", "text": "折價券管理"},
                            "style": "primary",
                            "color": HAL_PINK
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🧙‍♂️ 召喚南瓜巫師（管理員）", "text": "呼叫管理員"},
                            "style": "secondary",
                            "color": HAL_WHITE
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🌟 最新萬聖快訊！限時開啟！", "text": "活動快訊"},
                            "style": "primary",
                            "color": HAL_ORANGE
                        }
                    ]
                }
            ]
        }
    }

    return FlexSendMessage(
        alt_text="中秋節主功能選單",
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