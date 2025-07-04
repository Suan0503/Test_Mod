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

def get_menu_carousel():
    """
    產生主功能選單的 Flex Message（兩頁，內容集中管理）
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
                    "text": "🌸 茗殿功能選單 1/2",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": "#7D5FFF"
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
                                "label": "📱 驗證資訊",
                                "text": "驗證資訊"
                            },
                            "style": "primary",
                            "color": "#FFB6B6"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🎁 每日抽獎",
                                "text": "每日抽獎"
                            },
                            "style": "primary",
                            "color": "#A3DEE6"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "📬 預約諮詢",
                                "uri": choose_link()
                            },
                            "style": "primary",
                            "color": "#B889F2"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "📅 每日班表",
                                "uri": "https://t.me/+LaFZixvTaMY3ODA1"
                            },
                            "style": "secondary",
                            "color": "#FFF8B7"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "🌸 茗殿討論區",
                                "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
                            },
                            "style": "primary",
                            "color": "#FFDCFF"
                        }
                    ]
                }
            ]
        }
    })

    # 第二頁（折價券管理、查詢規則位置已更動）
    bubbles.append({
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "🌸 茗殿功能選單 2/2",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": "#7D5FFF"
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
                                "label": "💰 折價券管理",
                                "text": "折價券管理"
                            },
                            "style": "primary",
                            "color": "#A3DEA6"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "📖 查詢規則",
                                "text": "規則查詢"
                            },
                            "style": "secondary",
                            "color": "#C8C6A7"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🛎️ 呼叫管理員",
                                "text": "呼叫管理員"
                            },
                            "style": "secondary",
                            "color": "#B1E1FF"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "🔔 活動快訊",
                                "text": "活動快訊"
                            },
                            "style": "primary",
                            "color": "#FFC2C2"
                        }
                    ]
                }
            ]
        }
    })

    return FlexSendMessage(
        alt_text="主功能選單",
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )

def reply_with_menu(token, text=None):
    """
    統一回覆主選單與可選的說明文字
    """
    msgs = []
    if text:
        msgs.append(TextSendMessage(text=text))
    msgs.append(get_menu_carousel())
    line_bot_api.reply_message(token, msgs)

def notify_admins(user_id, display_name=None):
    """
    呼叫管理員功能：發訊息給所有管理員ID
    """
    mention = f"來自用戶ID：{user_id}"
    if display_name:
        mention = f"來自 {display_name}（{user_id}）"
    msg = f"🛎️ 有人呼叫管理員！\n{mention}\n請盡快協助處理。"
    for admin_id in ADMIN_IDS:
        try:
            line_bot_api.push_message(admin_id, TextSendMessage(text=msg))
        except Exception as e:
            print(f"通知管理員失敗：{admin_id}，錯誤：{e}")
