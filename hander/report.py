from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent, TextSendMessage
)
from extensions import line_bot_api, db
from models import Whitelist, Coupon
from utils.temp_users import temp_users
from storage import ADMIN_IDS
import re, time
from datetime import datetime, timedelta
import pytz

# ★ 新增：SQL 輔助
from sqlalchemy import text, func, cast, Integer
from sqlalchemy.exc import IntegrityError

report_pending_map = {}

# ★ 新增：簡易網址規範化（lower 主機、去 www、去追蹤參數、去 fragment、收斂結尾斜線）
def normalize_url(u: str) -> str:
    try:
        u = u.strip()
    except Exception:
        return u
    # 粗略處理（避免額外依賴）：只要符合 http(s) 就做基本正規化
    # 交由 DB 層做補強沒關係
    try:
        from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
        DROP_PARAMS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid","utm_id"}
        p = urlparse(u)
        scheme = (p.scheme or "http").lower()
        netloc = (p.netloc or "").lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k not in DROP_PARAMS]
        q.sort()
        path = p.path or "/"
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")
        return urlunparse((scheme, netloc, path, p.params, urlencode(q), ""))  # fragment 清空
    except Exception:
        return u

def _next_monthly_report_no(tz):
    """查本月最大 report_no，回傳下一個 3 碼字串（001 起）。來源：public.report_article"""
    now = datetime.now(tz)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if month_start.month == 12:
        next_month_start = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month_start = month_start.replace(month=month_start.month + 1)

    sql = text("""
        SELECT MAX(NULLIF(report_no,'')::int) AS max_no
        FROM public.report_article
        WHERE created_at >= :m_start
          AND created_at <  :m_next
          AND type = 'report'
    """)
    max_no = db.session.execute(sql, {"m_start": month_start, "m_next": next_month_start}).scalar()
    nxt = (max_no or 0) + 1
    return f"{nxt:03d}"

def handle_report(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    tz = pytz.timezone("Asia/Taipei")
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
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

    # 用戶取消／提交網址
    if user_id in temp_users and temp_users[user_id].get("report_pending"):
        if user_text == "取消":
            temp_users.pop(user_id, None)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="已取消回報流程，回到主選單！")
            )
            return

        url = user_text.strip()
        if not re.match(r"^https?://", url):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入正確的網址格式（必須以 http:// 或 https:// 開頭）\n如需取消，請輸入「取消」")
            )
            return

        # 會員資訊（顯示用）
        wl = Whitelist.query.filter_by(line_user_id=user_id).first()
        user_number = wl.id if wl else None
        user_lineid = wl.line_id if wl else ""

        # ★ 雙重驗證：規範化網址 → 查 public.report_article 是否已存在（全域 or 同人同址）
        url_norm = normalize_url(url)

        # 先查是否全域已有人回報過
        sql_chk_global = text("SELECT id, status, report_no FROM public.report_article WHERE url_norm = :u LIMIT 1")
        existed = db.session.execute(sql_chk_global, {"u": url_norm}).fetchone()
        if existed:
            status_map = {"pending":"審核中","approved":"已通過","rejected":"未通過"}
            st = status_map.get(existed.status, "處理中") if hasattr(existed, "status") else "處理中"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"這個網址之前已被回報，狀態：{st}（編號：{existed.report_no or '-'}）。\n請改貼其他網址喔～")
            )
            temp_users.pop(user_id, None)
            return

        # 同一用戶同一網址
        sql_chk_user = text("""
            SELECT id FROM public.report_article
            WHERE line_user_id = :uid AND url_norm = :u LIMIT 1
        """)
        existed_u = db.session.execute(sql_chk_user, {"uid": user_id, "u": url_norm}).fetchone()
        if existed_u:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="您已回報過這個網址囉～請改貼其他網址唷。")
            )
            temp_users.pop(user_id, None)
            return

        # ★ 產 report_no（每月 001 起）
        report_no_str = _next_monthly_report_no(tz)

        # 寫入 public.report_article 一筆 pending 紀錄（同表單）
        now = datetime.now(tz)
        today = now.date().isoformat()
        sql_insert = text("""
            INSERT INTO public.report_article
            (line_user_id, nickname, member_id, line_id, url, url_norm, status, created_at, date, report_no, type, amount)
            VALUES
            (:line_user_id, :nickname, :member_id, :line_id, :url, :url_norm, 'pending', :created_at, :date, :report_no, 'report', 0)
            RETURNING id
        """)
        try:
            new_id = db.session.execute(sql_insert, {
                "line_user_id": user_id,
                "nickname": display_name,
                "member_id": user_number,
                "line_id": user_lineid,
                "url": url,
                "url_norm": url_norm,
                "created_at": now,
                "date": today,
                "report_no": report_no_str
            }).scalar()
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # 可能被他人同時插入了同網址，友善提示
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="這個網址剛剛已被回報～請改貼其他網址唷。")
            )
            temp_users.pop(user_id, None)
            return

        short_text = f"網址：{url}" if len(url) < 55 else "新回報文，請點選按鈕處理"
        detail_text = (
            f"【用戶回報文】編號-{report_no_str}\n"
            f"暱稱：{display_name}\n"
            f"用戶編號：{user_number or ''}\n"
            f"LINE ID：{user_lineid}\n"
            f"網址：{url}"
        )

        # 建立 in-memory 對應，綁定 DB 記錄 id
        report_id = f"{user_id}_{int(time.time()*1000)}"
        for admin_id in ADMIN_IDS:
            report_pending_map[report_id] = {
                "user_id": user_id,
                "admin_id": admin_id,
                "display_name": display_name,
                "user_number": user_number or "",
                "user_lineid": user_lineid,
                "url": url,
                "url_norm": url_norm,
                "report_no": report_no_str,
                "record_db_id": new_id
            }
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
            line_bot_api.push_message(admin_id, TextSendMessage(text=detail_text))

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="✅ 已收到您的回報，管理員會盡快處理！")
        )
        temp_users.pop(user_id)
        return

    # 管理員填寫拒絕原因
    if user_id in temp_users and temp_users[user_id].get("report_ng_pending"):
        report_id = temp_users[user_id]["report_ng_pending"]
        info = report_pending_map.get(report_id)
        if info:
            reason = user_text
            to_user_id = info["user_id"]
            reply = f"❌ 您的回報文未通過審核，原因如下：\n{reason}"

            # ★ 更新資料庫：標記 rejected
            rec_id = info.get("record_db_id")
            if rec_id:
                try:
                    sql_reject = text("""
                        UPDATE public.report_article
                        SET status='rejected', reject_reason=:reason
                        WHERE id=:id AND status='pending'
                    """)
                    db.session.execute(sql_reject, {"reason": reason, "id": rec_id})
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print("更新回報狀態(rejected)失敗", e)

            try:
                line_bot_api.push_message(to_user_id, TextSendMessage(text=reply))
            except Exception as e:
                print("推播用戶回報拒絕失敗", e)

            temp_users.pop(user_id)
            report_pending_map.pop(report_id, None)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已將原因回傳給用戶。"))
        else:
            temp_users.pop(user_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到該回報資料（可能已處理過或超時）"))
        return

def handle_report_postback(event):
    user_id = event.source.user_id
    data = event.postback.data
    tz = pytz.timezone("Asia/Taipei")

    if data.startswith("report_ok|"):
        report_id = data.split("|")[1]
        info = report_pending_map.get(report_id)
        if info:
            to_user_id = info["user_id"]
            report_no = info.get("report_no", "未知")
            rec_id = info.get("record_db_id")
            reply = f"🟢 您的回報文已審核通過，獲得一張月底抽獎券！（編號：{report_no}）"

            # ★ DB：標記 approved（同表）
            try:
                now = datetime.now(tz)
                sql_ok = text("""
                    UPDATE public.report_article
                    SET status='approved', approved_at=:approved_at, approved_by=:approved_by
                    WHERE id=:id AND status='pending'
                """)
                db.session.execute(sql_ok, {
                    "approved_at": now,
                    "approved_by": user_id,  # 管理員 LINE user_id
                    "id": rec_id
                })
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("更新回報狀態(approved)失敗", e)

            # ★ 兼容舊流程：建立一張 Coupon(type='report', amount=0)（若尚未存在）
            try:
                today = datetime.now(tz).strftime("%Y-%m-%d")
                existed = Coupon.query.filter_by(
                    line_user_id=to_user_id, type="report", report_no=report_no
                ).first()
                if not existed:
                    new_coupon = Coupon(
                        line_user_id=to_user_id,
                        amount=0,  # 回報券金額預設 0，月底抽獎再更新
                        date=today,
                        created_at=datetime.now(tz),
                        report_no=report_no,
                        type="report"
                    )
                    db.session.add(new_coupon)
                    db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("建立兼容 Coupon 失敗", e)

            try:
                line_bot_api.push_message(to_user_id, TextSendMessage(text=reply))
            except Exception as e:
                print("推播用戶通過回報文失敗", e)

            report_pending_map.pop(report_id, None)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已通過並回覆用戶。"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="該回報已處理過或超時"))
        return

    elif data.startswith("report_ng|"):
        report_id = data.split("|")[1]
        info = report_pending_map.get(report_id)
        if info:
            temp_users[user_id] = {"report_ng_pending": report_id}
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入不通過的原因："))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="該回報已處理過或超時"))
        return
