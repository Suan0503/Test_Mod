from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent, TextSendMessage
)
from extensions import line_bot_api, db
from models import Whitelist, Coupon
from utils.temp_users import temp_users
from storage import ADMIN_IDS
import re, time
from datetime import datetime
import pytz

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

report_pending_map = {}

# —— 工具：網址規範化（有就用，沒欄位也不會炸）——
def normalize_url(u: str) -> str:
    try:
        from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
        DROP = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid","utm_id"}
        p = urlparse((u or "").strip())
        scheme = (p.scheme or "http").lower()
        netloc = (p.netloc or "").lower()
        if netloc.startswith("www."): netloc = netloc[4:]
        q = [(k,v) for k,v in parse_qsl(p.query, keep_blank_values=True) if k not in DROP]
        q.sort()
        path = p.path or "/"
        if path != "/" and path.endswith("/"): path = path.rstrip("/")
        return urlunparse((scheme, netloc, path, p.params, urlencode(q), ""))  # fragment 清空
    except Exception:
        return u

# —— 工具：偵測欄位是否存在（避免 UndefinedColumn）——
def has_url_norm_column() -> bool:
    try:
        row = db.session.execute(text("""
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name='report_article' AND column_name='url_norm'
        """)).fetchone()
        return bool(row)
    except Exception:
        return False

# —— 工具：每月流水號（沒有 url_norm 也能用）——
def next_monthly_report_no(tz):
    now = datetime.now(tz)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month_start = month_start.replace(year=month_start.year + 1, month=1) if month_start.month == 12 else month_start.replace(month=month_start.month + 1)
    max_no = db.session.execute(text("""
        SELECT MAX(NULLIF(report_no,'')::int) AS max_no
        FROM public.report_article
        WHERE created_at >= :ms AND created_at < :nx AND type='report'
    """), {"ms": month_start, "nx": next_month_start}).scalar()
    return f"{(max_no or 0)+1:03d}"

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
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已取消回報流程，回到主選單！"))
            return

        url = user_text.strip()
        if not re.match(r"^https?://", url):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確的網址格式（必須以 http:// 或 https:// 開頭）\n如需取消，請輸入「取消」"))
            return

        wl = Whitelist.query.filter_by(line_user_id=user_id).first()
        user_number = wl.id if wl else None
        user_lineid = wl.line_id if wl else ""

        url_norm = normalize_url(url)
        USE_URL_NORM = has_url_norm_column()

        # —— 查重（有 url_norm 欄位就用它，沒有就退化用 url）——
        if USE_URL_NORM:
            existed = db.session.execute(
                text("SELECT id, status, report_no FROM public.report_article WHERE url_norm = :u LIMIT 1"),
                {"u": url_norm}
            ).fetchone()
        else:
            existed = db.session.execute(
                text("SELECT id, status, report_no FROM public.report_article WHERE url = :u LIMIT 1"),
                {"u": url}
            ).fetchone()

        if existed:
            st = getattr(existed, "status", "處理中")
            rn = getattr(existed, "report_no", None) or "-"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"這個網址之前已被回報，狀態：{st}（編號：{rn}）。\n請改貼其他網址喔～"))
            temp_users.pop(user_id, None)
            return

        # 同人同址
        if USE_URL_NORM:
            existed_u = db.session.execute(
                text("SELECT id FROM public.report_article WHERE line_user_id=:uid AND url_norm=:u LIMIT 1"),
                {"uid": user_id, "u": url_norm}
            ).fetchone()
        else:
            existed_u = db.session.execute(
                text("SELECT id FROM public.report_article WHERE line_user_id=:uid AND url=:u LIMIT 1"),
                {"uid": user_id, "u": url}
            ).fetchone()
        if existed_u:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="您已回報過這個網址囉～請改貼其他網址唷。"))
            temp_users.pop(user_id, None)
            return

        # 產編號 & 寫入
        report_no_str = next_monthly_report_no(tz)
        now = datetime.now(tz)
        today = now.date().isoformat()

        if USE_URL_NORM:
            sql_insert = text("""
                INSERT INTO public.report_article
                (line_user_id, nickname, member_id, line_id, url, url_norm, status, created_at, date, report_no, type, amount)
                VALUES
                (:line_user_id, :nickname, :member_id, :line_id, :url, :url_norm, 'pending', :created_at, :date, :report_no, 'report', 0)
                RETURNING id
            """)
            params = {
                "line_user_id": user_id, "nickname": display_name, "member_id": user_number, "line_id": user_lineid,
                "url": url, "url_norm": url_norm, "created_at": now, "date": today, "report_no": report_no_str
            }
        else:
            # 沒有 url_norm 欄位時的退化插入
            sql_insert = text("""
                INSERT INTO public.report_article
                (line_user_id, nickname, member_id, line_id, url, status, created_at, date, report_no, type, amount)
                VALUES
                (:line_user_id, :nickname, :member_id, :line_id, :url, 'pending', :created_at, :date, :report_no, 'report', 0)
                RETURNING id
            """)
            params = {
                "line_user_id": user_id, "nickname": display_name, "member_id": user_number, "line_id": user_lineid,
                "url": url, "created_at": now, "date": today, "report_no": report_no_str
            }

        try:
            new_id = db.session.execute(sql_insert, params).scalar()
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="這個網址剛剛已被回報～請改貼其他網址唷。"))
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

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ 已收到您的回報，管理員會盡快處理！"))
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

            rec_id = info.get("record_db_id")
            if rec_id:
                try:
                    db.session.execute(text("UPDATE public.report_article SET status='rejected', reject_reason=:r WHERE id=:i AND status='pending'"),
                                       {"r": reason, "i": rec_id})
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

            # 標記 approved
            try:
                now = datetime.now(tz)
                db.session.execute(text("""
                    UPDATE public.report_article
                    SET status='approved', approved_at=:a, approved_by=:adm
                    WHERE id=:i AND status='pending'
                """), {"a": now, "adm": user_id, "i": rec_id})
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("更新回報狀態(approved)失敗", e)

            # 兼容舊券表：補一張 Coupon(type='report', amount=0)（避免你現有列表壞掉）
            try:
                today = datetime.now(tz).strftime("%Y-%m-%d")
                exist = Coupon.query.filter_by(line_user_id=to_user_id, type="report", report_no=report_no).first()
                if not exist:
                    db.session.add(Coupon(
                        line_user_id=to_user_id, amount=0, date=today,
                        created_at=datetime.now(tz), report_no=report_no, type="report"
                    ))
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
