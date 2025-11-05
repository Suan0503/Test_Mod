# -*- coding: utf-8 -*-
from linebot.models import TextSendMessage, FlexSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS  # 管理員清單
from secrets import choice as secrets_choice

# ================= 魔法學院配色（可依喜好微調） - 現代化調整 =================
# 簡潔現代主題：深色底，輔以亮色強調，按鈕風格調整
MAG_BG_1   = "#212121"  # 深灰（頁1底，更現代）
MAG_BG_2   = "#121212"  # 幾乎黑（頁2底）
MAG_GOLD   = "#FFD700"  # 亮金色/強調
MAG_PARCH  = "#B0BEC5"  # 羊皮紙灰（輔助文字）
MAG_BURG   = "#E53935"  # 亮紅色（警示/主要操作）
MAG_EMER   = "#00C853"  # 亮綠色（成功/功能）
MAG_INDIGO = "#3F51B5"  # 亮藍色（主要按鈕）
MAG_PURPLE = "#8E24AA"  # 紫色（次要強調）
MAG_STEEL  = "#424242"  # 鋼灰（分隔線）

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

# ====== 廣告專區（魔法學院主題）======
def get_ad_menu():
    btn_primary   = MAG_INDIGO   # 亮藍色
    btn_secondary = MAG_PURPLE   # 紫色

    buttons = []
    for i, link in enumerate(JKF_LINKS):
        buttons.append({
            "type": "button",
            "action": {"type": "uri", "label": link["label"], "uri": link["url"]},
            "style": "primary",  # 白色文字
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
                "backgroundColor": MAG_BG_2,
                "paddingAll": "16px",
                "contents": [{
                    "type": "text",
                    "text": "✨ 茗殿廣告資訊站",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": MAG_GOLD
                }]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": MAG_BG_2,
                "spacing": "md",
                "contents": [
                    {"type": "separator", "color": MAG_STEEL},
                    {"type": "box", "layout": "vertical", "spacing": "sm", "margin": "lg", "contents": buttons}
                ]
            },
            "styles": {"body": {"separator": False}}
        }
    )

# ====== 魔法學院主選單（兩頁 Carousel）- **更新版** ======
def get_menu_carousel():
    # 按鈕顏色配置 (現代風格)
    COLOR_PRIMARY = MAG_INDIGO  # 亮藍色
    COLOR_SECONDARY = MAG_PURPLE # 紫色
    COLOR_ACTION = MAG_EMER     # 亮綠色
    COLOR_TELEGRAM = MAG_PARCH  # 輔助灰

    # 第一頁 - 現代深色主題
    page1 = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": MAG_BG_1,
            "paddingAll": "16px",
            "contents": [{
                "type": "text",
                "text": "🧭 學院導航選單 1/2",
                "weight": "bold",
                "align": "center",
                "size": "lg",
                "color": MAG_GOLD
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": MAG_BG_1,
            "spacing": "md",
            "contents": [
                {"type": "separator", "color": MAG_STEEL},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        # 1. 學籍驗證
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🔑 學籍驗證 (主選單)", "text": "驗證資訊"},
                            "style": "primary",
                            "color": COLOR_PRIMARY
                        },
                        # 2. 入學抽獎
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🎲 每日抽獎", "text": "每日抽獎"},
                            "style": "primary",
                            "color": COLOR_ACTION
                        },
                        # 3. 學員介紹 (廣告專區)
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "📜 學員介紹 (廣告)", "text": "廣告專區"},
                            "style": "primary",
                            "color": COLOR_SECONDARY
                        },
                        # 4. 班表占卜室 (URI)
                        {
                            "type": "button",
                            "action": {"type": "uri", "label": "🗓️ 班表占卜室", "uri": "https://t.me/+svlFjBpb4hxkYjFl"},
                            "style": "secondary",
                            "color": COLOR_TELEGRAM
                        },
                        # 5. 預約水晶球（總機）(URI)
                        {
                            "type": "button",
                            "action": {"type": "uri", "label": "🔮 預約水晶球 (總機)", "uri": choose_link()},
                            "style": "secondary",
                            "color": MAG_BURG # 紅色警示
                        }
                    ]
                }
            ]
        }
    }

    # 第二頁 - 現代深色主題
    page2 = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": MAG_BG_2,
            "paddingAll": "16px",
            "contents": [{
                "type": "text",
                "text": "🔧 學院工具箱 2/2",
                "weight": "bold",
                "align": "center",
                "size": "lg",
                "color": MAG_GOLD
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": MAG_BG_2,
            "spacing": "md",
            "contents": [
                {"type": "separator", "color": MAG_STEEL},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        # 1. 學院討論大廳 (URI)
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "💬 學院討論大廳",
                                "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
                            },
                            "style": "primary",
                            "color": COLOR_ACTION
                        },
                        # 2. 折價卷魔法袋 (Message) -> 原回報文位置替補
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "💰 折價卷魔法袋", "text": "折價券管理"},
                            "style": "primary",
                            "color": COLOR_PRIMARY
                        },
                        # 3. 呼叫管理員 (Message) -> **電話號碼顯示**
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "📞 聯繫管理員 (電話)", "text": "管理員電話"}, # 預設傳送 "管理員電話" 讓後端處理
                            "style": "primary",
                            "color": MAG_BURG # 紅色警示
                        },
                        # 4. 最新魔法快訊！ (Message)
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🌟 最新魔法快訊", "text": "活動快訊"},
                            "style": "primary",
                            "color": COLOR_SECONDARY
                        },
                        # 5. (移除原回報文) 預留一個空間或調整
                        # 此處直接使用剩餘的按鈕空間，或者如果需要固定五個按鈕，可以增加一個功能。
                        # 這裡我將第四個按鈕移到這裡，讓總數保持在五個（原系統五個+一個回主選單）
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🔮 學院資訊查詢", "text": "學院資訊"},
                            "style": "secondary",
                            "color": COLOR_TELEGRAM
                        }
                    ]
                }
            ]
        }
    }

    return FlexSendMessage(
        alt_text="魔法學院主功能選單",
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
# **此函式保持不變，因為它用於推播給管理員，而非使用者介面**
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

# **新增一個函式來處理使用者傳送 "管理員電話" 的情況 (需要後端配合)**
def reply_admin_phone(reply_token):
    PHONE_NUMBER = "0987346208"
    msg = (
        "📞 **管理員緊急聯絡電話**\n"
        f"請撥打：**{PHONE_NUMBER}**\n\n"
        "> 請注意，電話聯絡僅限緊急情況。\n"
        "> 一般問題請多利用選單功能。"
    )
    line_bot_api.reply_message(reply_token, [TextSendMessage(text=msg)])