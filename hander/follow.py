<<<<<<< HEAD
from linebot.models import FollowEvent, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from extensions import handler, line_bot_api

@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = (
        "歡迎加入🍵茗殿🍵\n"
        "\n"
        "📜 驗證流程如下：\n"
        "1️⃣ 閱讀規則後點擊『我同意規則』\n"
        "2️⃣ 依步驟輸入手機號與 LINE ID\n"
        "3️⃣ 上傳 LINE 個人檔案截圖\n"
        "4️⃣ 系統進行快速自動驗證\n"
        "5️⃣ 如無法辨識將交由客服人工處理\n"
        "\n"
        "✅ 完成驗證即可解鎖專屬客服＆預約功能💖"
=======
from extensions import line_bot_api
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction

def handle_follow(event):
    user_id = event.source.user_id
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception:
        display_name = "用戶"
    welcome_text = (
        f"歡迎 {display_name} 加入🍵茗殿🍵\n\n"
        "完成驗證即可使用「選單功能」查詢各項服務。\n"
        "⚠️ 小助手不提供預約詢價，請洽專屬總機。\n"
        "📣 選單內有「廣告/活動頁」可參考最新方案。"
>>>>>>> d4ddc685c6a5e9088fd8a3a674c86d8d13cdf262
    )
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="我同意，開始驗證", text="我同意規則"))
    ])
    line_bot_api.push_message(
        user_id,
        TextSendMessage(
            text=welcome_text,
            quick_reply=quick_reply
        )
    )
# ⭐ 只 import entrypoint（這會自動帶入各功能模組）
import hander.entrypoint
import hander.follow
import hander.image
