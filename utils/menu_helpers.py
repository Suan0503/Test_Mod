
from linebot.models import TextSendMessage, FlexSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS  # 管理員清單
import os
from typing import List, Dict, Any, Optional

# ────────────── 主題設定（可多主題/多語系） ──────────────
MENU_THEME = {
    "name": "學院祭",
    "main_bg1": "#254D7A",     # 學院藍
    "main_bg2": "#F5F5F5",     # 學院白
    "btn_gold": "#FFD700",     # 學院金
    "btn_green": "#3CB371",    # 學院綠
    "btn_blue": "#254D7A",     # 學院藍
    "btn_white": "#FFFFFF",    # 純白
    "btn_red": "#E53935",      # 學院紅
    "btn_orange": "#FF9800",   # 活力橘
    "btn_gray": "#B0BEC5",     # 淺灰
    "btn_purple": "#7C4DFF",   # 活力紫
    "alt_text": "🎓 學院祭主功能選單",
    "carousel_titles": ["🎓 學院祭主選單 1/2", "🏫 學院祭主選單 2/2"],
    "carousel_title_colors": ["#FFD700", "#254D7A"],
}

# ────────────── 主選單按鈕資料化 ──────────────
MENU_BUTTONS: List[List[Dict[str, Any]]] = [
    [
        {"label": "🎫 學院驗證資訊", "type": "message", "text": "驗證資訊", "color": "btn_gold", "style": "primary"},
        {"label": "🎉 學院抽獎", "type": "message", "text": "每日抽獎", "color": "btn_green", "style": "primary"},
        {"label": "🏆 學院祭活動專區", "type": "message", "text": "廣告專區", "color": "btn_blue", "style": "primary"},
        {"label": "📅 活動班表查詢", "type": "uri", "uri": "https://t.me/+svlFjBpb4hxkYjFl", "color": "btn_white", "style": "secondary"},
        {"label": "🗓️ 預約諮詢", "type": "uri", "uri": None, "color": "btn_orange", "style": "secondary", "dynamic_uri": True},
    ],
    [
        {"label": "🏛️ 學院討論區", "type": "uri", "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default", "color": "btn_green", "style": "primary"},
        {"label": "📝 活動回報(暫停)", "type": "message", "text": "回報文", "color": "btn_purple", "style": "primary"},
        {"label": "💰 折價券管理", "type": "message", "text": "折價券管理", "color": "btn_red", "style": "primary"},
        {"label": "🧑‍🎓 呼叫管理員(暫停)", "type": "message", "text": "呼叫管理員", "color": "btn_gray", "style": "secondary"},
        {"label": "🎈 活動快訊(暫停)", "type": "message", "text": "活動快訊", "color": "btn_orange", "style": "primary"},
    ]
]

# ────────────── 主選單產生函式 ──────────────
def build_menu_bubble(page: int) -> Dict[str, Any]:
    theme = MENU_THEME
    buttons = []
    for btn in MENU_BUTTONS[page]:
        color = theme[btn["color"]]
        action = None
        if btn["type"] == "message":
            action = {"type": "message", "label": btn["label"], "text": btn["text"]}
        elif btn["type"] == "uri":
            uri = btn.get("uri")
            if btn.get("dynamic_uri"):
                uri = choose_link()
            action = {"type": "uri", "label": btn["label"], "uri": uri}
        buttons.append({
            "type": "button",
            "action": action,
            "style": btn["style"],
            "color": color
        })
    return {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "backgroundColor": theme["main_bg1"] if page == 0 else theme["main_bg2"],
            "contents": [
                {
                    "type": "text",
                    "text": theme["carousel_titles"][page],
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": theme["carousel_title_colors"][page]
                },
                {"type": "separator", "color": theme["btn_gray"]},
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

def get_menu_carousel() -> FlexSendMessage:
    """
    主功能選單，主題/按鈕資料化，易於維護與擴充
    """
    bubbles = [build_menu_bubble(0), build_menu_bubble(1)]
    return FlexSendMessage(
        alt_text=MENU_THEME["alt_text"],
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )

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
        "label": "茗殿 - 主頁推薦",
        "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"
    },
    {
        "label": "泰式料理菜單 - 1",
        "url": "https://www.jkforum.net/p/thread-16422277-1-1.html"
    },
    {
        "label": "泰式料理菜單 - 2",
        "url": "https://www.jkforum.net/p/thread-17781450-1-1.html"
    },
    {
        "label": "越式料理小吃 - 1",
        "url": "https://www.jkforum.net/p/thread-18976516-1-1.html"
    },
    {
        "label": "越式料理小吃 - 2",
        "url": "https://www.jkforum.net/p/thread-17742482-1-1.html"
    },
    {
        "label": "檔期推薦 - 多多",
        "url": "https://www.jkforum.net/p/thread-20296958-1-1.html"
    },
    {
        "label": "檔期推薦 - 莎莎",
        "url": "https://www.jkforum.net/p/thread-20296970-1-1.html"
    },
    {
        "label": "檔期推薦 - 心心",
        "url": "https://www.jkforum.net/p/thread-10248540-1-1.html"
    },
    {
        "label": "本期空缺中",
        "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"
    },
    {
        "label": "本期空缺中",
        "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"
    },
]

def get_ad_menu():
    """
    廣告專區 Flex Message，10個JKF連結按鈕（名稱可獨立修改），
    主副色跳色，所有按鈕皆為白色字體。
    """
    buttons = []
    btn_primary = "#2C4A6B"   # 深藍
    btn_secondary = "#4B99C2" # 深天藍

    for i, link in enumerate(JKF_LINKS):
        buttons.append({
            "type": "button",
            "action": {
                "type": "uri",
                "label": link["label"],
                "uri": link["url"]
            },
            "style": "primary",  # 全部主色，確保字體白色
            "color": btn_primary if i % 2 == 0 else btn_secondary
        })
    # 回主選單按鈕
    buttons.append({
        "type": "button",
        "action": {
            "type": "message",
            "label": "🏠 回主選單",
            "text": "主選單"
        },
        "style": "primary",
        "color": btn_secondary
    })
    return FlexSendMessage(
        alt_text="廣告專區",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "backgroundColor": "#1C2636",  # 深夏夜藍
                "contents": [
                    {
                        "type": "text",
                        "text": "🏖️ 夏日廣告專區",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center",
                        "color": "#FFD700"    # 金黃
                    },
                    {"type": "separator", "color": "#31485C"},
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
    主功能選單，深色夏日風格
    """
    # 學院祭主題色系
    main_bg1 = "#254D7A"     # 學院藍
    main_bg2 = "#F5F5F5"     # 學院白
    btn_gold = "#FFD700"     # 學院金
    btn_green = "#3CB371"    # 學院綠
    btn_blue = "#254D7A"     # 學院藍
    btn_white = "#FFFFFF"    # 純白
    btn_red = "#E53935"      # 學院紅
    btn_orange = "#FF9800"   # 活力橘
    btn_gray = "#B0BEC5"     # 淺灰
    btn_purple = "#7C4DFF"   # 活力紫

    bubbles = []

    # 第一頁
    bubbles.append({
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "backgroundColor": main_bg1,
            "contents": [
                {
                    "type": "text",
                    "text": "� 學院祭主選單 1/2",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": btn_gold
                },
                {"type": "separator", "color": btn_gray},
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
                                "label": "� 學院驗證資訊",
                                "text": "驗證資訊"
                            },
                            "style": "primary",
                            "color": btn_gold
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "� 學院抽獎",
                                "text": "每日抽獎"
                            },
                            "style": "primary",
                            "color": btn_green
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🏆 學院祭活動專區",
                                "text": "廣告專區"
                            },
                            "style": "primary",
                            "color": btn_blue
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "📅 活動班表查詢",
                                "uri": "https://t.me/+svlFjBpb4hxkYjFl"
                            },
                            "style": "secondary",
                            "color": btn_white
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "�️ 預約諮詢",
                                "uri": choose_link()
                            },
                            "style": "secondary",
                            "color": btn_orange
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
            "backgroundColor": main_bg2,
            "contents": [
                {
                    "type": "text",
                    "text": "� 學院祭主選單 2/2",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": btn_blue
                },
                {"type": "separator", "color": btn_gray},
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
                                "label": "�️ 學院討論區",
                                "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
                            },
                            "style": "primary",
                            "color": btn_green
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "📝 活動回報(暫停)",
                                "text": "回報文"
                            },
                            "style": "primary",
                            "color": btn_purple
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "� 折價券管理",
                                "text": "折價券管理"
                            },
                            "style": "primary",
                            "color": btn_red
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "�‍🎓 呼叫管理員(暫停)",
                                "text": "呼叫管理員"
                            },
                            "style": "secondary",
                            "color": btn_gray
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "� 活動快訊(暫停)",
                                "text": "活動快訊"
                            },
                            "style": "primary",
                            "color": btn_orange
                        }
                    ]
                }
            ]
        }
    })

    return FlexSendMessage(
        alt_text="� 學院祭主功能選單",
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )

def reply_with_menu(token: str, text: Optional[str] = None) -> None:
    """
    回覆主選單與可選的說明文字
    """
    msgs: List[Any] = []
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
