from flask import Blueprint
from extensions import handler, line_bot_api, db
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, TextSendMessage, PostbackEvent
from models import Whitelist, Coupon
from utils.draw_utils import save_coupon_record
from storage import ADMIN_IDS
import pytz
from datetime import datetime

report_bp = Blueprint('report', __name__)

# 暫存回報文狀態
report_pending = {}

def now_str():
    return datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y/%m/%d %H:%M:%S")

@handler.add(MessageEvent, message=TextMessage)
def handle_report_message(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception:
        display_name = "用戶"

    # 回報文登記流程
    if user_text in ["回報文", "回報文登記"]:
        report_pending[user_id] = {"step": "wait_url"}
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請貼上您的回報文網址"))
        return

    if user_id in report_pending and report_pending[user_id].get("step") == "wait_url":
        url = user_text.strip()
        wl = Whitelist.query.filter_by(line_user_id=user_id).first()
        user_number = wl.id if wl else ""
        lineid = wl.line_id if wl else ""
        dt = now_str()
        report_pending[user_id] = {
            "step": "wait_admin",
            "url": url, "dt": dt, "display_name": display_name,
            "user_number": user_number, "line_id": lineid
        }
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已收取回報文，請等待管理員確認"))
        flex = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": f"- {dt} 回報文確認 -", "weight": "bold", "size": "lg", "align": "center", "color": "#7D5FFF"},
                    {"type": "separator"},
                    {"type": "text", "text": f"暱稱：{display_name}"},
                    {"type": "text", "text": f"用戶編號：{user_number}"},
                    {"type": "text", "text": f"LINE ID：{lineid}"},
                    {"type": "text", "text": f"回報文網址：\n{url}"}
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "spacing": "md",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "正確",
                            "data": f"REPORT_OK::{user_id}"
                        },
                        "style": "primary",
                        "color": "#A3DEA6"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "取消",
                            "data": f"REPORT_CANCEL::{user_id}"
                        },
                        "style": "primary",
                        "color": "#FFB6B6"
                    }
                ]
            }
        }
        for admin_id in ADMIN_IDS:
            line_bot_api.push_message(admin_id, FlexSendMessage(alt_text="回報文確認", contents=flex))
        return

    # 管理員輸入取消原因
    if user_id in ADMIN_IDS:
        for uid, info in report_pending.items():
            if info.get("step") == "wait_cancel_reason" and info.get("wait_cancel_for_admin") == user_id:
                reason = user_text.strip()
                try:
                    line_bot_api.push_message(uid, TextSendMessage(text=f"❌ 您的回報文被取消，原因如下：\n{reason}"))
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已發送原因給用戶"))
                except Exception as e:
                    print("發送取消原因失敗：", e)
                report_pending.pop(uid, None)
                return

@handler.add(PostbackEvent)
def handle_report_postback(event):
    data = event.postback.data
    if data.startswith("REPORT_OK::"):
        user_id = data.split("::")[1]
        try:
            amount = 100
            save_coupon_record(user_id, amount, Coupon, db)
            line_bot_api.push_message(user_id, TextSendMessage(text="✅ 您的回報文已審核通過，並獲得一張抽獎券！"))
        except Exception as e:
            print(e)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已發送通過通知與抽獎券"))
        report_pending.pop(user_id, None)
        return

    if data.startswith("REPORT_CANCEL::"):
        user_id = data.split("::")[1]
        if user_id in report_pending:
            report_pending[user_id]["step"] = "wait_cancel_reason"
            report_pending[user_id]["wait_cancel_for_admin"] = event.source.user_id
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入取消原因，將回覆給用戶"))
        return
