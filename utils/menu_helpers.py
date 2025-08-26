"""
選單與廣告相關工具
"""
from linebot.models import TextSendMessage, FlexSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS
import os

def choose_link():
    group = [
        "https://line.me/ti/p/g7TPO_lhAL",
        "https://line.me/ti/p/emkjaMQkMK",
        "https://line.me/ti/p/AKRUvSCLRC"
    ]
    return group[hash(os.urandom(8)) % len(group)]

JKF_LINKS = [
    {"label": "茗殿 - 主頁推薦", "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"},
    {"label": "泰式料理菜單 - 1", "url": "https://www.jkforum.net/p/thread-16422277-1-1.html"},
    {"label": "泰式料理菜單 - 2", "url": "https://www.jkforum.net/p/thread-17781450-1-1.html"},
    {"label": "越式料理小吃 - 1", "url": "https://www.jkforum.net/p/thread-18976516-1-1.html"},
    {"label": "越式料理小吃 - 2", "url": "https://www.jkforum.net/p/thread-17742482-1-1.html"},
    {"label": "檔期推薦 - 多多", "url": "https://www.jkforum.net/p/thread-20296958-1-1.html"},
    {"label": "檔期推薦 - 莎莎", "url": "https://www.jkforum.net/p/thread-20296970-1-1.html"},
    {"label": "檔期推薦 - 心心", "url": "https://www.jkforum.net/p/thread-10248540-1-1.html"},
    {"label": "本期空缺中", "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"},
    {"label": "本期空缺中", "url": "https://www.jkforum.net/p/thread-15744749-1-1.html"},
]

def get_ad_menu():
    buttons = []
    btn_primary = "#2C4A6B"
    btn_secondary = "#4B99C2"
    for i, link in enumerate(JKF_LINKS):
        buttons.append({
            "type": "button",
            "action": {
                "type": "uri",
                "label": link["label"],
                "uri": link["url"]
            },
            "style": "primary",
            "color": btn_primary if i % 2 == 0 else btn_secondary
        })
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
                "backgroundColor": "#1C2636",
                "contents": [
                    {
                        "type": "text",
                        "text": "廣告專區",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#FFFFFF"
                    },
                    {"type": "separator"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": buttons
                    }
                ]
            }
        }
    )

def reply_with_menu(reply_token, text):
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

def notify_admins(text):
    for admin_id in ADMIN_IDS:
        line_bot_api.push_message(admin_id, TextSendMessage(text=text))

def reply_with_ad_menu(reply_token):
    line_bot_api.reply_message(reply_token, get_ad_menu())
