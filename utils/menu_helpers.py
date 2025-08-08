from linebot.models import TextSendMessage, FlexSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS  # 管理員清單
import os

def choose_link():
    group = [
        "https://line.me/ti/p/g7TPO_lhAL",
        "https://line.me/ti/p/emkjaMQkMK",
        "https://line.me/ti/p/AKRUvSCLRC"
    ]
    return group[hash(os.urandom(8)) % len(group)]

# === JKF 廣告連結與名稱可獨立修改 ===
JKF_LINKS = [
    {
        "label": "JKF 廣告一",
        "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"
    },
    {
        "label": "JKF 廣告二",
        "url": "https://www.jkforum.net/p/thread-16422277-1-1.html"
    },
    {
        "label": "JKF 廣告三",
        "url": "https://www.jkforum.net/p/thread-17781450-1-1.html"
    },
    {
        "label": "JKF 廣告四",
        "url": "https://www.jkforum.net/p/thread-18976516-1-1.html"
    },
    {
        "label": "JKF 廣告五",
        "url": "https://www.jkforum.net/p/thread-17742482-1-1.html"
    },
    {
        "label": "JKF 廣告六",
        "url": "https://www.jkforum.net/thread-6-1-1.html"
    },
    {
        "label": "JKF 廣告七",
        "url": "https://www.jkforum.net/thread-7-1-1.html"
    },
    {
        "label": "JKF 廣告八",
        "url": "https://www.jkforum.net/thread-8-1-1.html"
    },
    {
        "label": "JKF 廣告九",
        "url": "https://www.jkforum.net/thread-9-1-1.html"
    },
    {
        "label": "JKF 廣告十",
        "url": "https://www.jkforum.net/thread-10-1-1.html"
    },
]

def get_ad_menu():
    """
    廣告專區 Flex Message，10個JKF連結按鈕（名稱可獨立修改）
    """
    buttons = []
    for i, link in enumerate(JKF_LINKS):
        buttons.append({
            "type": "button",
            "action": {
                "type": "uri",
                "label": link["label"],
                "uri": link["url"]
            },
            "style": "primary" if i % 2 == 0 else "secondary",
            "color": "#53CFE9" if i % 2 == 0 else "#FFFCE6"
        })
    return FlexSendMessage(
        alt_text="廣告專區",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "backgroundColor": "#E3FDFD",
                "contents": [
                    {"type": "text", "text": "🏖️ 夏日廣告專區", "weight": "bold", "size": "lg", "align": "center", "color": "#3BC9DB"},
                    {"type": "separator"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": buttons
                    }
                ]
            }
        }
    )

def get_menu_carousel():
    """
    主功能選單，夏日海灘風格，按鈕順序已依需求調整
    """
    bubbles = []

    # 第一頁
    bubbles.append({
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "backgroundColor": "#A7E9FF",  # 海灘天空藍
            "contents": [
                {
                    "type": "text",
                    "text": "🏖️ 夏日茗殿選單 1/2",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": "#1E90FF"
                },
                {"type": "separator"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🍧 開啟主選單",
                                "text": "驗證資訊"
                            },
                            "style": "primary",
                            "color": "#FFEB99"  # 沙灘黃
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🌴 每日抽獎",
                                "text": "每日抽獎"
                            },
                            "style": "primary",
                            "color": "#00CFC1"  # 海水綠
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "📢 廣告專區",
                                "text": "廣告專區"
                            },
                            "style": "primary",
                            "color": "#53CFE9"  # 清涼藍
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "📅 班表查詢",
                                "uri": "https://t.me/+LaFZixvTaMY3ODA1"
                            },
                            "style": "secondary",
                            "color": "#FFFCE6"  # 沙灘白
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "🕶️ 預約諮詢",
                                "uri": choose_link()
                            },
                            "style": "secondary",
                            "color": "#FFD6B0"  # 橘沙
                        }
                    ]
                }
            ]
        }
    })

    # 第二頁
    bubbles.append({
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "backgroundColor": "#FFECCF",  # 沙灘米色
            "contents": [
                {
                    "type": "text",
                    "text": "🏝️ 夏日茗殿選單 2/2",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": "#F6A500"
                },
                {"type": "separator"},
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
                            "color": "#B5EAD7"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "📝 回報文登記",
                                "text": "回報文"
                            },
                            "style": "primary",
                            "color": "#F7B7A3"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "💸 折價券管理",
                                "text": "折價券管理"
                            },
                            "style": "primary",
                            "color": "#A3DEA6"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🧊 呼叫管理員",
                                "text": "呼叫管理員"
                            },
                            "style": "secondary",
                            "color": "#B1E1FF"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🌞 活動快訊",
                                "text": "活動快訊"
                            },
                            "style": "primary",
                            "color": "#FFBCBC"
                        }
                    ]
                }
            ]
        }
    })

    return FlexSendMessage(
        alt_text="🏖️ 夏日主功能選單",
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )

def reply_with_menu(token, text=None):
    """
    回覆主選單與可選的說明文字
    """
    msgs = []
    if text:
        msgs.append(TextSendMessage(text=text))
    msgs.append(get_menu_carousel())
    line_bot_api.reply_message(token, msgs)

def reply_with_ad_menu(token):
    """
    回覆廣告專區選單
    """
    msgs = [get_ad_menu()]
    line_bot_api.reply_message(token, msgs)

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
