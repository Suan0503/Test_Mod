from linebot.models import MessageEvent, TextMessage, PostbackEvent, TextSendMessage
from extensions import handler, line_bot_api, db
from utils.menu_helpers import reply_with_menu, notify_admins
from hander.report import handle_report, handle_report_postback
from hander.admin import handle_admin
from hander.verify import handle_verify
from utils.temp_users import temp_users
from models import Whitelist, Coupon
import pytz
from datetime import datetime

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

    # 驗證資訊
    if user_text == "驗證資訊":
        tz = pytz.timezone("Asia/Taipei")
        user = Whitelist.query.filter_by(line_user_id=user_id).first()
        if user:
            reply = (
                f"📱 {user.phone}\n"
                f"🌸 暱稱：{user.name or '未登記'}\n"
                f"       個人編號：{user.id}\n"
                f"🔗 LINE ID：{user.line_id or '未登記'}\n"
                f"🕒 {user.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"✅ 驗證成功，歡迎加入茗殿\n"
                f"🌟 加入密碼：ming666"
            )
        else:
            reply = "查無你的驗證資訊，請先完成驗證流程。"
        reply_with_menu(event.reply_token, reply)
        return

    # 折價券管理
    if user_text in ["折價券管理", "券紀錄", "我的券紀錄"]:
        tz = pytz.timezone("Asia/Taipei")
        now = datetime.now(tz)
        today_str = now.strftime('%Y-%m-%d')
        month_str = now.strftime('%Y-%m')

        # 今日每日抽獎
        today_draw = Coupon.query.filter_by(
            line_user_id=user_id, date=today_str, type="draw"
        ).first()
        # 本月回報文
        month_reports = Coupon.query.filter(
            Coupon.line_user_id == user_id,
            Coupon.type == "report",
            Coupon.date.startswith(month_str)
        ).all()

        reply_lines = []
        if today_draw:
            reply_lines.append("🎁 今日的每日抽獎：已獲得折價券！")
        else:
            reply_lines.append("🎁 今日的每日抽獎：尚未抽獎或未中獎")

        if month_reports:
            reply_lines.append(f"📝 本月回報文折價券：{len(month_reports)} 張")
        else:
            reply_lines.append("📝 本月回報文折價券：0 張")

        reply = "\n".join(reply_lines)
        reply_with_menu(event.reply_token, reply)
        return

    # 主選單/功能選單/每日抽獎/查詢規則/活動快訊
    if user_text in [
        "主選單", "功能選單", "選單", "menu", "Menu",
        "每日抽獎", "查詢規則", "規則查詢", "活動快訊"
    ]:
        reply_with_menu(event.reply_token)
        return

    # 呼叫管理員
    if user_text in ["呼叫管理員"]:
        display_name = None
        try:
            profile = line_bot_api.get_profile(user_id)
            display_name = profile.display_name
        except Exception:
            pass
        notify_admins(user_id, display_name)
        reply_with_menu(event.reply_token, "已通知管理員，請稍候，主選單如下：")
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
