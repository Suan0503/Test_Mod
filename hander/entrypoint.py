from linebot.models import MessageEvent, TextMessage, PostbackEvent
from extensions import handler
from hander.menu import handle_menu
from hander.report import handle_report, handle_report_postback
from hander.admin import handle_admin
from hander.verify import handle_verify

@handler.add(MessageEvent, message=TextMessage)
def entrypoint(event):
    user_text = event.message.text.strip()

    # 最高優先權：回報文流程（如果用戶在回報文流程中）
    # 檢查 temp_users 狀態
    from utils.temp_users import temp_users
    user_id = event.source.user_id
    if user_id in temp_users and (
        temp_users[user_id].get("report_pending") or
        temp_users[user_id].get("report_ng_pending")
    ):
        handle_report(event)
        return

    # 回報文關鍵字
    if user_text in ["回報文", "Report", "report"]:
        handle_report(event)
        return

    # 管理員指令
    if user_text.startswith("/msg "):
        handle_admin(event)
        return

    # 主選單、抽獎、驗證資訊等
    if user_text in ["主選單", "功能選單", "選單", "menu", "Menu", "每日抽獎", "驗證資訊"]:
        handle_menu(event)
        return

    # 其餘交給驗證流程
    handle_verify(event)

@handler.add(PostbackEvent)
def entrypoint_postback(event):
    # 將回報文的 postback 交給 handle_report_postback
    data = event.postback.data
    if data.startswith("report_ok|") or data.startswith("report_ng|"):
        handle_report_postback(event)
        return
    # 其他 postback 邏輯（如有）
