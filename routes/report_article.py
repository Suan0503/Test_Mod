from flask import Blueprint, request, abort, jsonify
from extensions import db
from models import ReportArticle, Whitelist
from models.report_article import ReportArticle
from utils.report_approve_flex import get_admin_approve_flex
from datetime import datetime, timedelta
import pytz

ADMIN_USER_IDS = [
    "Uea1646aa1a57861c85270d846aaee0eb",  # 換成你的管理員 LINE ID
]

report_bp = Blueprint('report', __name__)
pending_reject_reason = {}

@handler.add(MessageEvent, message=TextMessage)
def handle_report_article(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()

    # 用戶觸發 "回報文"
    if user_text == "回報文":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請貼上JKF文章網址（如：https://jktank.net/5312191/611130218812768）"))
        return

    # 用戶貼了網址
    if user_text.startswith("https://jktank.net/"):
        user = Whitelist.query.filter_by(line_user_id=user_id).first()
        if not user:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先完成驗證才能參加回報文活動"))
            return

        report = ReportArticle(
            line_user_id=user.line_user_id,
            nickname=user.name,
            member_id=user.id,
            line_id=user.line_id,
            url=user_text,
            status="pending",
        )
        db.session.add(report)
        db.session.commit()

        for admin_id in ADMIN_USER_IDS:
            flex = get_admin_approve_flex(report, admin_id)
            line_bot_api.push_message(admin_id, flex)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已收到您的回報文，請稍候管理員審核！"))
        return

    # 管理員填寫拒絕原因
    if user_id in pending_reject_reason:
        report_id = pending_reject_reason[user_id]
        report = ReportArticle.query.get(report_id)
        if report and report.status == "pending":
            report.status = "rejected"
            report.reject_reason = user_text
            db.session.commit()
            msg = (
                f"🌸 暱稱：{report.nickname}\n"
                f"      個人編號：{report.member_id}\n"
                f"🔗 LINE ID：{report.line_id}\n"
                f"網址：{report.url}\n"
                f"\nX回報文審核不通過X\n原因：{user_text}"
            )
            line_bot_api.push_message(report.line_user_id, TextSendMessage(text=msg))
            del pending_reject_reason[user_id]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已發送拒絕理由給用戶"))
        return

@handler.add(PostbackEvent)
def handle_report_approve_postback(event):
    data = event.postback.data
    user_id = event.source.user_id

    if data.startswith("report_approve:"):
        _, report_id, admin_id = data.split(":")
        report = ReportArticle.query.get(int(report_id))
        if report and report.status == "pending":
            now = datetime.now(pytz.timezone("Asia/Taipei"))
            first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (first_of_month + timedelta(days=32)).replace(day=1)
            count = ReportArticle.query.filter(
                ReportArticle.status=="approved",
                ReportArticle.created_at >= first_of_month,
                ReportArticle.created_at < next_month
            ).count() + 1
            ticket_code = f"{now.strftime('%Y%m')}{count:03d}"

            report.status = "approved"
            report.approved_at = now
            report.approved_by = admin_id
            report.ticket_code = ticket_code
            db.session.commit()

            msg = (
                f"🌸 暱稱：{report.nickname}\n"
                f"      個人編號：{report.member_id}\n"
                f"🔗 LINE ID：{report.line_id}\n"
                f"網址：{report.url}\n\n"
                f"回報文已通過 獲得回報文限定抽獎券\n"
                f"{now.month}/{now.day} {report.nickname} 回報抽獎{ticket_code[-3:]}"
            )
            line_bot_api.push_message(report.line_user_id, TextSendMessage(text=msg))
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已通過並發券"))

    elif data.startswith("report_reject:"):
        _, report_id, admin_id = data.split(":")
        pending_reject_reason[user_id] = int(report_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入拒絕原因，會發送給用戶！"))
