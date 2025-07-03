from linebot.models import MessageEvent, TextMessage, PostbackEvent, TextSendMessage
from extensions import handler, line_bot_api
from hander.menu import handle_menu
from hander.report import handle_report, handle_report_postback
from hander.admin import handle_admin
from hander.verify import handle_verify
from utils.temp_users import temp_users

@handler.add(MessageEvent, message=TextMessage)
def entrypoint(event):
    user_text = event.message.text.strip()
    user_id = event.source.user_id

    # 回報文流程進行中（pending 狀態）
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

    # 主選單、抽獎、驗證資訊、券紀錄等
    if user_text in [
        "主選單", "功能選單", "選單", "menu", "Menu",
        "每日抽獎", "驗證資訊", "券紀錄", "我的券紀錄"
    ]:
        handle_menu(event)
        return

    # 其餘交給驗證流程
    handle_verify(event)

@handler.add(PostbackEvent)
def entrypoint_postback(event):
    data = event.postback.data
    user_id = event.source.user_id

    if data.startswith("report_ok|") or data.startswith("report_ng|"):
        handle_report_postback(event)
        return

    # 處理 OCR 驗證失敗時「申請手動驗證」的 Postback
    if data == "manual_verify":
        record = temp_users.get(user_id)
        if not record:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="請先輸入手機號碼開始驗證流程。")
            )
            return
        record["step"] = "waiting_confirm"
        temp_users[user_id] = record
        reply = (
            f"📱 {record['phone']}\n"
            f"🌸 暱稱：{record['name']}\n"
            f"       個人編號：待驗證後產生\n"
            f"🔗 LINE ID：{record['line_id']}\n"
            f"（此用戶經手動通過）\n"
            f"請問以上資料是否正確？正確請回復 1\n"
            f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 你可在這裡加更多其他 Postback 邏輯
