# -*- coding: utf-8 -*-
from linebot.models import TextSendMessage, FlexSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS  # 管理員清單
import os
from typing import List, Dict, Any, Optional

# ────────────── Emoji（用 Unicode Escape 防亂碼） ──────────────
class E:
    CAP = "\U0001F393"                # 🎓
    SCHOOL = "\U0001F3EB"             # 🏫
    TICKET = "\U0001F39F"             # 🎟/🎫（Admission Tickets）
    PARTY = "\U0001F389"              # 🎉
    TROPHY = "\U0001F3C6"             # 🏆
    CAL = "\U0001F4C5"                # 📅
    NOTE = "\U0001F4DD"               # 📝
    MONEY_BAG = "\U0001F4B0"          # 💰
    STUDENT = "\U0001F9D1\u200D\U0001F393"  # 🧑‍🎓
    BALLOON = "\U0001F388"            # 🎈
    DIAMOND = "\u2756"                # ❖
    HOME = "\U0001F3E0"               # 🏠

# ────────────── 主題設定（學院風配色） ──────────────
MENU_THEME = {
    "name": "學院祭",
    # 核心學院風：海軍藍 / 典雅金 / 象牙白
    "main_bg1": "#1E2A44",     # 深海軍藍（首頁）
    "main_bg2": "#F8F6EF",     # 象牙白（次頁）
    "btn_gold": "#C9A227",     # 典雅金
    "btn_green": "#2E7D32",    # 校園綠
    "btn_blue": "#1E2A44",     # 海軍藍
    "btn_white": "#FFFFFF",    # 純白
    "btn_red": "#B23A48",      # 勳章紅（更沈穩）
    "btn_orange": "#CC7A00",   # 暖橘（較內斂）
    "btn_gray": "#B0BEC5",     # 淺灰
    "btn_purple": "#6A5ACD",   # 斯文紫
    "alt_text": f"{E.CAP} 學院祭主功能選單",
    "carousel_titles": [f"{E.DIAMOND} 學院祭主選單 1/2", f"{E.DIAMOND} 學院祭主選單 2/2"],
    "carousel_title_colors": ["#C9A227", "#1E2A44"],
}

# ────────────── 主選單按鈕資料化 ──────────────
MENU_BUTTONS: List[List[Dict[str, Any]]] = [
    [
        {"label": f"{E.TICKET} 學生證查詢（主選單）", "type": "message", "text": "驗證資訊", "color": "btn_gold", "style": "primary"},
        {"label": f"{E.PARTY} 福利社優惠（抽獎）", "type": "message", "text": "每日抽獎", "color": "btn_green", "style": "primary"},
        # 學院祭活動專區：按鈕改成典雅金邊（primary+深藍），更學院風
        {"label": f"{E.TROPHY} 資優學生介紹（廣告）", "type": "message", "text": "廣告專區", "color": "btn_gold", "style": "primary"},
        {"label": f"{E.CAL} 課表查詢（班表）", "type": "uri", "uri": "https://t.me/+svlFjBpb4hxkYjFl", "color": "btn_white", "style": "secondary"},
        {"label": "🗓️ 點我找老師（總機）", "type": "uri", "uri": None, "color": "btn_orange", "style": "secondary", "dynamic_uri": True},
    ],
    [
        {"label": f"🏛️ 學院討論區（聊天群）", "type": "uri", "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default", "color": "btn_green", "style": "primary"},
        {"label": f"{E.NOTE} 活動回報(暫停)", "type": "message", "text": "回報文", "color": "btn_purple", "style": "primary"},
        {"label": f"{E.MONEY_BAG} 折價券管理", "type": "message", "text": "折價券管理", "color": "btn_red", "style": "primary"},
        {"label": f"{E.STUDENT} 報告教官(暫停)", "type": "message", "text": "呼叫管理員", "color": "btn_gray", "style": "secondary"},
        {"label": f"{E.BALLOON} 活動快訊(暫停)", "type": "message", "text": "活動快訊", "color": "btn_orange", "style": "primary"},
    ]
]

# ────────────── 主選單產生 ──────────────
def build_menu_bubble(page: int) -> Dict[str, Any]:
    theme = MENU_THEME
    buttons = []
    for btn in MENU_BUTTONS[page]:
        color = theme[btn["color"]]
        # action
        if btn["type"] == "message":
            action = {"type": "message", "label": btn["label"], "text": btn["text"]}
        elif btn["type"] == "uri":
            uri = btn.get("uri")
            if btn.get("dynamic_uri"):
                uri = choose_link()
            action = {"type": "uri", "label": btn["label"], "uri": uri}
        else:
            action = {"type": "message", "label": btn["label"], "text": "未定義"}
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
    主功能選單（學院風）
    - 解決亂碼（emoji 以 Unicode escape 表示）
    - 單一定義（避免重複覆蓋）
    """
    bubbles = [build_menu_bubble(0), build_menu_bubble(1)]
    return FlexSendMessage(
        alt_text=MENU_THEME["alt_text"],
        contents={"type": "carousel", "contents": bubbles}
    )

def choose_link():
    group = [
        "https://line.me/ti/p/g7TPO_lhAL",
        "https://line.me/ti/p/emkjaMQkMK",
        "https://line.me/ti/p/AKRUvSCLRC"
    ]
    return group[hash(os.urandom(8)) % len(group)]

# === JKF 廣告連結與名稱（可獨立修改） ===
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

def get_ad_menu() -> FlexSendMessage:
    """
    廣告專區 Flex Message（學院風重設）
    - 背景：更深的學院藍
    - 按鈕：海軍藍 / 典雅金 交錯，白字，高對比
    - 標題：金色，置中
    """
    buttons = []
    btn_primary = "#1E2A44"   # 海軍藍
    btn_alt_gold = "#C9A227"  # 典雅金（按鈕底）
    text_white = "#FFFFFF"

    for i, link in enumerate(JKF_LINKS):
        color = btn_primary if i % 2 == 0 else btn_alt_gold
        buttons.append({
            "type": "button",
            "action": {"type": "uri", "label": link["label"], "uri": link["url"]},
            "style": "primary",
            "color": color
        })

    # 回主選單
    buttons.append({
        "type": "button",
        "action": {"type": "message", "label": f"{E.HOME} 回主選單", "text": "主選單"},
        "style": "primary",
        "color": btn_primary
    })

    return FlexSendMessage(
        alt_text="廣告專區",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "backgroundColor": "#141C2B",  # 更深的學院藍，凸顯按鈕
                "contents": [
                    {
                        "type": "text",
                        "text": f"{E.CAP} 夏日廣告專區",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center",
                        "color": "#C9A227"
                    },
                    {"type": "separator", "color": "#2B3A57"},
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

# ────────────── 封裝：回覆主選單 / 廣告專區 / 通知管理員 ──────────────
def reply_with_menu(token: str, text: Optional[str] = None) -> None:
    msgs: List[Any] = []
    if text:
        msgs.append(TextSendMessage(text=text))
    msgs.append(get_menu_carousel())
    line_bot_api.reply_message(token, msgs)

def reply_with_ad_menu(token) -> None:
    msgs = [get_ad_menu()]
    line_bot_api.reply_message(token, msgs)

def notify_admins(user_id: str, display_name: Optional[str] = None) -> None:
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