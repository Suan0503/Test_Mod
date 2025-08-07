from linebot.models import TextSendMessage, FlexSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS  # 管理員清單
import os

def get_ad_menu():
    """
    廣告專區 Flex Message，10個JKF連結按鈕（點擊直接打開網址）
    """
    jkf_links = [
        "https://www.jkforum.net/thread-1-1-1.html",
        "https://www.jkforum.net/thread-2-1-1.html",
        "https://www.jkforum.net/thread-3-1-1.html",
        "https://www.jkforum.net/thread-4-1-1.html",
        "https://www.jkforum.net/thread-5-1-1.html",
        "https://www.jkforum.net/thread-6-1-1.html",
        "https://www.jkforum.net/thread-7-1-1.html",
        "https://www.jkforum.net/thread-8-1-1.html",
        "https://www.jkforum.net/thread-9-1-1.html",
        "https://www.jkforum.net/thread-10-1-1.html",
    ]
    buttons = []
    for i, link in enumerate(jkf_links):
        buttons.append({
            "type": "button",
            "action": {
                "type": "uri",
                "label": f"JKF 廣告 {i+1}",
                "uri": link
            },
            "style": "primary" if i % 2 == 0 else "secondary",
            "color": "#FF5E5B" if i % 2 == 0 else "#FFD6E0"
        })
    return FlexSendMessage(
        alt_text="廣告專區",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": "📢 廣告專區", "weight": "bold", "size": "lg", "align": "center", "color": "#FF5E5B"},
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
    主功能選單（已將規則查詢改為廣告專區）
    """
    bubbles = []

    # 第一頁
    bubbles.append({
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "🌴 夏日茗殿選單 1/2",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": "#0099CC"
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
                                "label": "🍧 驗證資訊",
                                "text": "驗證資訊"
                            },
                            "style": "primary",
                            "color": "#66D8C2"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🎁 夏日抽獎",
                                "text": "每日抽獎"
                            },
                            "style": "primary",
                            "color": "#FFD166"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "🕶️ 預約諮詢",
                                "uri": choose_link()
                            },
                            "style": "primary",
                            "color": "#F4978E"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "📅 夏季班表",
                                "uri": "https://t.me/+LaFZixvTaMY3ODA1"
                            },
                            "style": "secondary",
                            "color": "#FFF2A6"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "🌺 討論區",
                                "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
                            },
                            "style": "primary",
                            "color": "#B5EAD7"
                        }
                    ]
                }
            ]
        }
    })

    # 第二頁，規則查詢→廣告專區
    bubbles.append({
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "🌊 夏日茗殿選單 2/2",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": "#0099CC"
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
                                "label": "📢 廣告專區",
                                "text": "廣告專區"
                            },
                            "style": "secondary",
                            "color": "#E8F6EF"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🧊 管理員幫幫我",
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
        alt_text="🌴 夏日主功能選單",
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
