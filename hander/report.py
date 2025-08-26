from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent, TextSendMessage
)
from extensions import line_bot_api, db
# 明確從子模組匯入，避免 models.__init__ 的延遲匯入或循環問題
from models.whitelist import Whitelist
from models.coupon import Coupon
from utils.temp_users import temp_users
from storage import ADMIN_IDS
import re, time, logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

# report_pending_map: report_id -> info dict
report_pending_map = {}

def handle_report(event):
    # 安全取 user_id 與文字內容（避免在群組/聊天室或非文字事件時崩潰）
    user_id = getattr(event.source, "user_id", None)
    user_text = (getattr(event.message, "text", "") or "").strip()
    tz = pytz.timezone("Asia/Taipei")

    try:
        profile = line_bot_api.get_profile(user_id) if user_id else None
        display_name = profile.display_name if profile else "用戶"
    except Exception:
        display_name = "用戶"

    # 啟動回報流程
    if user_text in ["回報文", "Report", "report"]:
        temp_users[user_id] = {"report_pending": True}
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入要回報的網址（請直接貼網址）：\n\n如需取消，請輸入「取消」")
        )
        return

    # 用戶取消或提交回報流程
    if user_id in temp_users and temp_users[user_id].get("report_pending"):
        if user_text == "取消":
            temp_users.pop(user_id, None)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="已取消回報流程，回到主選單！")
            )
            return

        url = user_text
        if not re.match(r"^https?://", url):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入正確的網址格式（必須以 http:// 或 https:// 開頭）\n如需取消，請輸入「取消」")
            )
            return

        # 找出回報者在白名單的資料（若有）
        wl = Whitelist.query.filter_by(line_user_id=user_id).first() if user_id else None
        user_number = wl.id if wl else ""
        user_lineid = wl.line_id if wl else ""

        # 取得最後一筆有 report_no 的 coupon，計算下一個編號
        try:
            last_coupon = Coupon.query.filter(Coupon.report_no != None).order_by(Coupon.id.desc()).first()
        except Exception:
            # 若 DB 查詢失敗，記錄錯誤並 fallback 編號為 1
            logger.exception("查詢最後一筆 coupon 時發生錯誤")
            last_coupon = None

        if last_coupon and getattr(last_coupon, "report_no", None) and str(last_coupon.report_no).isdigit():
            report_no = int(last_coupon.report_no) + 1
        else:
            report_no = 1
        report_no_str = f"{report_no:03d}"

        short_text = f"網址：{url}" if len(url) < 55 else "新回報文，請點選按鈕處理"
        detail_text = (
            f"【用戶回報文】編號-{report_no_str}\n"
            f"暱稱：{display_name}\n"
            f"用戶編號：{user_number}\n"
            f"LINE ID：{user_lineid}\n"
            f"網址：{url}"
        )

        # 建立唯一 report_id（只建立一次），並將資訊寫入一次（避免在迴圈內重覆覆寫）
        report_id = f"{user_id}_{int(time.time()*1000)}"
        report_info = {
            "user_id": user_id,
            "display_name": display_name,
            "user_number": user_number,
            "user_lineid": user_lineid,
            "url": url,
            "report_no": report_no_str,
            # 可以加上 admins list，或其他需要的 meta
            "admins": list(ADMIN_IDS),
            "created_at": datetime.now(tz),
        }
        report_pending_map[report_id] = report_info

        # 通知每位管理員（在迴圈外已儲存 report_info）
        for admin_id in ADMIN_IDS:
            try:
                line_bot_api.push_message(
                    admin_id,
                    TemplateSendMessage(
                        alt_text="收到用戶回報文",
                        template=ButtonsTemplate(
                            title="收到新回報文",
                            text=short_text,
                            actions=[
                                PostbackAction(label="🟢 O", data=f"report_ok|{report_id}"),
                                PostbackAction(label="❌ X", data=f"report_ng|{report_id}")
                            ]
                        )
                    )
                )
                # 傳詳細文字給管理員（方便快速查看）
                line_bot_api.push_message(admin_id, TextSendMessage(text=detail_text))
            except Exception:
                logger.exception("推播管理員失敗（report 通知）")

        # 回覆用戶
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="✅ 已收到您的回報，管理員會盡快處理！")
        )
        temp_users.pop(user_id, None)
        return

    # 管理員填寫拒絕原因（當管理員在先前點了 ❌ 後，把 reason 輸入）
    if user_id in temp_users and temp_users[user_id].get("report_ng_pending"):
        report_id = temp_users[user_id]["report_ng_pending"]
        info = report_pending_map.get(report_id)
        # 清除 pending（避免重複處理）
        temp_users.pop(user_id, None)
        if info:
            reason = user_text
            to_user_id = info.get("user_id")
            reply = f"❌ 您的回報文未通過審核，原因如下：\n{reason}"
            try:
                if to_user_id:
                    line_bot_api.push_message(to_user_id, TextSendMessage(text=reply))
            except Exception:
                logger.exception("推播用戶回報拒絕失敗")
            # 移除該回報資料
            report_pending_map.pop(report_id, None)
            # 告知管理員已回傳
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已將原因回傳給用戶。"))
        else:
            # 找不到該回報資料（可能已處理或逾時）
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到該回報資料（可能已處理過或超時）"))
        return

def handle_report_postback(event):
    user_id = getattr(event.source, "user_id", None)
    data = getattr(event.postback, "data", "") if getattr(event, "postback", None) else ""
    if not data:
        return

    # 管理員審核通過
    if data.startswith("report_ok|"):
        report_id = data.split("|", 1)[1]
        info = report_pending_map.get(report_id)
        if info:
            to_user_id = info.get("user_id")
            report_no = info.get("report_no", "未知")
            reply = f"🟢 您的回報文已審核通過，獲得一張月底抽獎券！（編號：{report_no}）"
            try:
                tz = pytz.timezone("Asia/Taipei")
                today = datetime.now(tz).strftime("%Y-%m-%d")
                # 新增 coupon（以現有 model 欄位為準）
                new_coupon = Coupon(
                    # 維持與現有程式一致的欄位名稱：line_user_id
                    line_user_id=to_user_id,
                    amount=0,  # 預設為 0，實際中獎時再改金額
                    date=today,
                    created_at=datetime.now(tz),
                    report_no=report_no,
                    type="report"
                )
                db.session.add(new_coupon)
                db.session.commit()
                try:
                    if to_user_id:
                        line_bot_api.push_message(to_user_id, TextSendMessage(text=reply))
                except Exception:
                    logger.exception("推播用戶通過回報文失敗（通知用戶）")
            except Exception:
                logger.exception("寫入 coupon 或推播用戶時發生錯誤")
                try:
                    db.session.rollback()
                except Exception:
                    pass
            # 移除該 pending
            report_pending_map.pop(report_id, None)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已通過並回覆用戶。"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="該回報已處理過或超時"))
        return

    # 管理員選擇不通過（先要求輸入原因）
    elif data.startswith("report_ng|"):
        report_id = data.split("|", 1)[1]
        info = report_pending_map.get(report_id)
        if info:
            # 將管理員導入下一步輸入拒絕原因的狀態
            temp_users[user_id] = {"report_ng_pending": report_id}
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入不通過的原因："))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="該回報已處理過或超時"))
        return
