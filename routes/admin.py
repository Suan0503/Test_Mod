import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Whitelist, Blacklist, TempVerify, StoredValueWallet, StoredValueTransaction
from utils.db_utils import update_or_create_whitelist_from_data
from hander.verify import EXTRA_NOTICE
from linebot.models import TextSendMessage
from extensions import line_bot_api
from extensions import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 常數：Dashboard 顯示筆數
DASHBOARD_LIMIT = int(os.getenv('DASHBOARD_LIMIT', '20'))


def load_dashboard_data():
    whitelists = Whitelist.query.order_by(Whitelist.created_at.desc()).limit(DASHBOARD_LIMIT).all()
    blacklists = Blacklist.query.order_by(Blacklist.created_at.desc()).limit(DASHBOARD_LIMIT).all()
    tempverifies = (TempVerify.query
            .filter(TempVerify.status == 'pending',
                TempVerify.phone.isnot(None), TempVerify.phone != '',
                TempVerify.line_id.isnot(None), TempVerify.line_id != '')
            .order_by(TempVerify.created_at.desc())
            .limit(DASHBOARD_LIMIT).all())
    return whitelists, blacklists, tempverifies

def render_dashboard(whitelists=None, blacklists=None, tempverifies=None):
    if whitelists is None:
        whitelists = Whitelist.query.order_by(Whitelist.created_at.desc()).limit(DASHBOARD_LIMIT).all()
    if blacklists is None:
        blacklists = Blacklist.query.order_by(Blacklist.created_at.desc()).limit(DASHBOARD_LIMIT).all()
    if tempverifies is None:
        # 僅顯示「待驗證」且有輸入手機與 LINE ID 的資料
        tempverifies = (TempVerify.query
                        .filter(TempVerify.status == 'pending',
                                TempVerify.phone.isnot(None), TempVerify.phone != '',
                                TempVerify.line_id.isnot(None), TempVerify.line_id != '')
                        .order_by(TempVerify.created_at.desc())
                        .limit(DASHBOARD_LIMIT).all())
    return render_template('admin_dashboard.html', whitelists=whitelists, blacklists=blacklists, tempverifies=tempverifies)

def render_home(whitelists=None, blacklists=None, tempverifies=None, active_tab=None):
    if whitelists is None or blacklists is None or tempverifies is None:
        base_wl, base_bl, base_tv = load_dashboard_data()
        if whitelists is None:
            whitelists = base_wl
        if blacklists is None:
            blacklists = base_bl
        if tempverifies is None:
            tempverifies = base_tv
    return render_template('admin_home.html', whitelists=whitelists, blacklists=blacklists, tempverifies=tempverifies, limit=DASHBOARD_LIMIT, active_tab=active_tab)


@admin_bp.route('/')
def admin_root():
    return redirect(url_for('admin.home'))

@admin_bp.route('/home')
def home():
    whitelists, blacklists, tempverifies = load_dashboard_data()
    active_tab = request.args.get('tab') or request.args.get('active_tab')
    return render_template('admin_home.html', whitelists=whitelists, blacklists=blacklists, tempverifies=tempverifies, limit=DASHBOARD_LIMIT, active_tab=active_tab)


@admin_bp.route('/dashboard')
def admin_dashboard():
    return render_dashboard()


# 白名單
@admin_bp.route('/whitelist/search')
def whitelist_search():
    q = request.args.get('q','').strip()
    view = request.args.get('view')
    if q:
        whitelists = Whitelist.query.filter(
            Whitelist.phone.like(f"%{q}%") |
            Whitelist.name.like(f"%{q}%") |
            Whitelist.line_id.like(f"%{q}%")
        ).order_by(Whitelist.created_at.desc()).limit(DASHBOARD_LIMIT).all()
    else:
        whitelists = None
    if view == 'home':
        return render_home(whitelists=whitelists, active_tab='whitelist')
    return render_dashboard(whitelists=whitelists)
@admin_bp.route('/whitelist/delete', methods=['POST'])
def whitelist_delete():
    phone = request.form.get('phone','').strip()
    w = Whitelist.query.filter_by(phone=phone).first()
    if not w:
        flash('找不到該白名單記錄','danger')
        return redirect(url_for('admin.home', tab='whitelist'))
    db.session.delete(w)
    db.session.commit()
    flash('白名單刪除成功','info')
    return redirect(url_for('admin.home', tab='whitelist'))


# 黑名單
@admin_bp.route('/blacklist/search')
def blacklist_search():
    q = request.args.get('q','').strip()
    view = request.args.get('view')
    if q:
        blacklists = Blacklist.query.filter(
            Blacklist.phone.like(f"%{q}%") |
            Blacklist.name.like(f"%{q}%")
        ).order_by(Blacklist.created_at.desc()).limit(DASHBOARD_LIMIT).all()
    else:
        blacklists = None
    if view == 'home':
        return render_home(blacklists=blacklists, active_tab='blacklist')
    return render_dashboard(blacklists=blacklists)


@admin_bp.route('/blacklist/add', methods=['POST'])
def blacklist_add():
    phone = request.form.get('phone','').strip()
    name = request.form.get('name','').strip()
    reason = request.form.get('reason','').strip()
    if not phone or not name or not reason:
        flash('黑名單新增資料不完整','warning')
        return redirect(url_for('admin.home', tab='blacklist'))
    if Blacklist.query.filter_by(phone=phone).first():
        flash('手機已存在於黑名單','warning')
        return redirect(url_for('admin.home', tab='blacklist'))
    b = Blacklist()
    b.phone = phone
    b.name = name
    b.reason = reason
    db.session.add(b)
    db.session.commit()
    flash('黑名單新增成功','success')
    return redirect(url_for('admin.home', tab='blacklist'))


@admin_bp.route('/blacklist/delete', methods=['POST'])
def blacklist_delete():
    phone = request.form.get('phone','').strip()
    b = Blacklist.query.filter_by(phone=phone).first()
    if not b:
        flash('找不到該黑名單記錄','danger')
        return redirect(url_for('admin.home', tab='blacklist'))
    db.session.delete(b)
    db.session.commit()
    flash('黑名單刪除成功','info')
    return redirect(url_for('admin.home', tab='blacklist'))


# 暫存名單（待驗證）
@admin_bp.route('/tempverify/verify', methods=['POST'])
def tempverify_verify():
    _id = request.form.get('id')
    tv = TempVerify.query.filter_by(id=_id).first()
    if not tv:
        flash('找不到暫存名單','danger')
        return redirect(url_for('admin.admin_dashboard'))
    # 將暫存資料寫入白名單（快速通關）
    try:
        data = {
            'phone': tv.phone,
            'name': tv.nickname,
            'line_id': tv.line_id,
        }
        record, _ = update_or_create_whitelist_from_data(data, user_id=tv.line_user_id, reverify=True)
        db.session.delete(tv)
        db.session.commit()
        flash(f'已通過並寫入白名單：{record.phone}','success')
        if record.line_user_id:
            try:
                msg = (
                    f"📱 {record.phone}\n"
                    f"🌸 暱稱：{record.name or '用戶'}\n"
                    f"🔗 LINE ID：{record.line_id or '未登記'}\n"
                    f"🕒 {record.created_at}\n"
                    f"✅ 驗證成功，歡迎加入茗殿\n"
                    f"🌟 加入密碼：ming666"
                ) + EXTRA_NOTICE
                line_bot_api.push_message(record.line_user_id, TextSendMessage(text=msg))
            except Exception:
                pass
    except Exception as e:
        db.session.rollback()
        flash(f'寫入白名單時發生錯誤：{e}','danger')
    return redirect(url_for('admin.home', tab='pending'))


@admin_bp.route('/tempverify/delete', methods=['POST'])
def tempverify_delete():
    _id = request.form.get('id')
    tv = TempVerify.query.filter_by(id=_id).first()
    if not tv:
        flash('找不到暫存名單','danger')
        return redirect(url_for('admin.admin_dashboard'))
    db.session.delete(tv)
    db.session.commit()
    flash('暫存名單刪除成功','info')
    return redirect(url_for('admin.home', tab='pending'))


@admin_bp.route('/schedule/')
def admin_schedule():
    return render_template('schedule.html')


# ========= 儲值金專區 =========
@admin_bp.route('/wallet')
def wallet_home():
    q = (request.args.get('q') or '').strip()
    wallet = None
    txns = []
    coupon_500_total = 0
    coupon_300_total = 0
    coupon_100_total = 0
    wl_user = None
    error = None
    if q:
        try:
            # 以手機或用戶編號查找
            wl = None
            if q.isdigit():
                try:
                    wl = Whitelist.query.filter((Whitelist.phone == q) | (Whitelist.id == int(q))).first()
                except Exception:
                    wl = Whitelist.query.filter_by(phone=q).first()
            else:
                wl = Whitelist.query.filter_by(phone=q).first()
            wallet = None
            if wl:
                wallet = StoredValueWallet.query.filter_by(whitelist_id=wl.id).first()
                if not wallet:
                    wallet = StoredValueWallet()
                    wallet.whitelist_id = wl.id
                    wallet.phone = wl.phone
                    wallet.balance = 0
                    db.session.add(wallet)
                    db.session.commit()
            else:
                wallet = StoredValueWallet.query.filter_by(phone=q).first()
                if not wallet and q.isdigit() and len(q) == 10 and q.startswith('09'):
                    wallet = StoredValueWallet()
                    wallet.phone = q
                    wallet.balance = 0
                    db.session.add(wallet)
                    db.session.commit()
            if wallet:
                # 近期交易
                txns = (StoredValueTransaction.query
                        .filter_by(wallet_id=wallet.id)
                        .order_by(StoredValueTransaction.created_at.desc())
                        .limit(100).all())
                # 轉換時間為台北時區字串
                try:
                    import pytz
                    tz = pytz.timezone('Asia/Taipei')
                    utc = pytz.utc
                    for _t in txns:
                        dt = getattr(_t, 'created_at', None)
                        if dt:
                            if dt.tzinfo is None:
                                dt = utc.localize(dt)
                            local_dt = dt.astimezone(tz)
                            _t.local_time_str = local_dt.strftime('%Y/%m/%d %H:%M')
                        else:
                            _t.local_time_str = ''
                except Exception:
                    for _t in txns:
                        _t.local_time_str = _t.created_at.strftime('%Y/%m/%d %H:%M') if _t.created_at else ''
                # 折價券總數（全量計算避免被limit影響）
                all_txns = StoredValueTransaction.query.filter_by(wallet_id=wallet.id).all()
                c500 = c300 = c100 = 0
                for t in all_txns:
                    sign = 1 if t.type == 'topup' else -1
                    c500 += sign * (t.coupon_500_count or 0)
                    c300 += sign * (t.coupon_300_count or 0)
                    # 可能舊資料無欄位
                    try:
                        c100 += sign * (getattr(t, 'coupon_100_count', 0) or 0)
                    except Exception:
                        pass
                coupon_500_total = max(c500, 0)
                coupon_300_total = max(c300, 0)
                coupon_100_total = max(c100, 0)
                # 用戶資訊（暱稱、LINE ID）
                try:
                    if wallet.whitelist_id:
                        wl_user = Whitelist.query.filter_by(id=wallet.whitelist_id).first()
                    elif wallet.phone:
                        wl_user = Whitelist.query.filter_by(phone=wallet.phone).first()
                except Exception:
                    wl_user = None
        except Exception as e:
            db.session.rollback()
            error = f"資料讀取錯誤，可能尚未執行遷移：{e}"
    return render_template('wallet.html', q=q, wallet=wallet, txns=txns, error=error,
                           coupon_500_total=coupon_500_total, coupon_300_total=coupon_300_total,
                           coupon_100_total=coupon_100_total, wl_user=wl_user)

@admin_bp.route('/wallet/summary')
def wallet_summary():
    """列出所有已有錢包的用戶：手機號碼 / 暱稱 / 編號 / 累計儲值金額 / 目前餘額 / 折價券(500/300/100)。支援手機搜尋。"""
    q = (request.args.get('q') or '').strip()
    base_query = StoredValueWallet.query
    if q:
        base_query = base_query.filter(StoredValueWallet.phone.like(f"%{q}%"))
    wallets = base_query.order_by(StoredValueWallet.created_at.asc()).all()
    rows = []
    import pytz
    tz = pytz.timezone('Asia/Taipei')
    for w in wallets:
        # 計算折價券總數
        txns = StoredValueTransaction.query.filter_by(wallet_id=w.id).all()
        c500 = c300 = c100 = 0
        for t in txns:
            sign = 1 if t.type == 'topup' else -1
            c500 += sign * (t.coupon_500_count or 0)
            c300 += sign * (t.coupon_300_count or 0)
            try:
                c100 += sign * (getattr(t, 'coupon_100_count', 0) or 0)
            except Exception:
                pass
        c500 = max(c500, 0)
        c300 = max(c300, 0)
        c100 = max(c100, 0)
        # 若餘額與所有折價券皆為 0，從總表隱藏
        if (w.balance or 0) == 0 and c500 == 0 and c300 == 0 and c100 == 0:
            continue
        wl = None
        if w.whitelist_id:
            wl = Whitelist.query.filter_by(id=w.whitelist_id).first()
        # 累計儲值：所有 topup 交易金額相加
        topups = StoredValueTransaction.query.filter_by(wallet_id=w.id, type='topup').all()
        total_topup = sum(t.amount for t in topups if t.amount)
        rows.append({
            'phone': w.phone,
            'nickname': (wl.name if wl and wl.name else '—'),
            'code': (wl.id if wl else '—'),
            'total_topup': total_topup,
            'balance': w.balance,
            'c500': c500,
            'c300': c300,
            'c100': c100,
            'created_at': w.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M') if w.created_at else ''
        })
    return render_template('wallet_summary.html', rows=rows, count=len(rows), q=q)

# ========= 儲值對帳（今日與區間） =========
@admin_bp.route('/wallet/reconcile')
def wallet_reconcile():
    """對帳報表：顯示今日儲值總額，並提供自訂日期區間查詢與明細、彙總。"""
    import pytz
    from datetime import datetime as _dt, timedelta
    tz = pytz.timezone('Asia/Taipei')

    # 取得查詢參數
    preset = (request.args.get('preset') or '').strip()  # today, yesterday, thisweek, thismonth
    start_str = (request.args.get('start') or '').strip()
    end_str = (request.args.get('end') or '').strip()
    export = (request.args.get('export') or '').strip()  # csv

    now_local = _dt.now(tz)

    def day_bounds_local(d):
        start_local = tz.localize(_dt(d.year, d.month, d.day, 0, 0, 0))
        end_local = start_local + timedelta(days=1)
        return start_local, end_local

    # 預設為今日
    if preset == 'yesterday':
        y = now_local.date() - timedelta(days=1)
        start_local, end_local = day_bounds_local(_dt(y.year, y.month, y.day))
    elif preset == 'thisweek':
        # 以週一為一週開始
        weekday = now_local.date().weekday()  # Monday=0
        monday = now_local.date() - timedelta(days=weekday)
        start_local = tz.localize(_dt(monday.year, monday.month, monday.day))
        end_local = tz.localize(_dt(now_local.year, now_local.month, now_local.day)) + timedelta(days=1)
    elif preset == 'thismonth':
        first = tz.localize(_dt(now_local.year, now_local.month, 1))
        # 下月一號
        if now_local.month == 12:
            next_first = tz.localize(_dt(now_local.year+1, 1, 1))
        else:
            next_first = tz.localize(_dt(now_local.year, now_local.month+1, 1))
        start_local, end_local = first, next_first
    else:
        # 若提供自訂起迄，採用自訂；否則今日
        if start_str:
            try:
                y, m, d = [int(x) for x in start_str.split('-')]
                start_local = tz.localize(_dt(y, m, d))
            except Exception:
                start_local = tz.localize(_dt(now_local.year, now_local.month, now_local.day))
        else:
            start_local = tz.localize(_dt(now_local.year, now_local.month, now_local.day))
        if end_str:
            try:
                y2, m2, d2 = [int(x) for x in end_str.split('-')]
                # end 選擇的日子 +1 天（半開區間）
                end_local = tz.localize(_dt(y2, m2, d2)) + timedelta(days=1)
            except Exception:
                end_local = start_local + timedelta(days=1)
        else:
            end_local = start_local + timedelta(days=1)

    # 轉為 UTC 以過濾（DB 使用 utcnow 建立時間）
    start_utc = start_local.astimezone(pytz.utc)
    end_utc = end_local.astimezone(pytz.utc)

    # 查詢 topup 交易
    q = (StoredValueTransaction.query
         .filter(StoredValueTransaction.type == 'topup')
         .filter(StoredValueTransaction.created_at >= start_utc)
         .filter(StoredValueTransaction.created_at < end_utc)
         .order_by(StoredValueTransaction.created_at.asc()))
    txns = q.all()

    # 明細與總計
    total_amount = sum(t.amount or 0 for t in txns)
    count = len(txns)
    avg_amount = (total_amount // count) if count else 0

    # 取得電話/姓名/代號與本地時間字串
    rows = []
    for t in txns:
        wallet = StoredValueWallet.query.filter_by(id=t.wallet_id).first()
        phone = wallet.phone if wallet else '—'
        wl = None
        nickname = '—'
        code = '—'
        if wallet and wallet.whitelist_id:
            wl = Whitelist.query.filter_by(id=wallet.whitelist_id).first()
            if wl:
                nickname = wl.name or '—'
                code = wl.id
        # 本地時間字串
        try:
            import pytz as _p
            utc = _p.utc
            dt = t.created_at
            if dt and dt.tzinfo is None:
                dt = utc.localize(dt)
            local_dt = dt.astimezone(tz) if dt else None
            time_str = local_dt.strftime('%Y/%m/%d %H:%M') if local_dt else ''
        except Exception:
            time_str = t.created_at.strftime('%Y/%m/%d %H:%M') if t.created_at else ''
        rows.append({
            'id': t.id,
            'time': time_str,
            'phone': phone,
            'nickname': nickname,
            'code': code,
            'amount': t.amount or 0,
            'remark': (t.remark or '')[:120],
        })

    # 依 remark 分組（可用於現金/轉帳等對帳）
    by_remark = {}
    for r in rows:
        k = r['remark'] or '—'
        by_remark.setdefault(k, {'amount': 0, 'count': 0})
        by_remark[k]['amount'] += r['amount']
        by_remark[k]['count'] += 1

    # 依日期（日）彙總
    by_day = {}
    for t in txns:
        dt = t.created_at
        if dt and dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        local_dt = dt.astimezone(tz) if dt else None
        day_key = local_dt.strftime('%Y-%m-%d') if local_dt else '—'
        by_day.setdefault(day_key, 0)
        by_day[day_key] += (t.amount or 0)

    # CSV 匯出
    if export == 'csv':
        import csv
        from io import StringIO
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['ID', '時間(台北)', '手機', '名稱', '編號', '金額', '備註'])
        for r in rows:
            cw.writerow([r['id'], r['time'], r['phone'], r['nickname'], r['code'], r['amount'], r['remark']])
        output = si.getvalue()
        from flask import Response
        filename = f"wallet_topups_{start_local.strftime('%Y%m%d')}_{(end_local - timedelta(days=1)).strftime('%Y%m%d')}.csv"
        return Response(output, mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename="{filename}"'})

    # 今日總額（便捷顯示）
    today_start_local = tz.localize(_dt(now_local.year, now_local.month, now_local.day))
    today_end_local = today_start_local + timedelta(days=1)
    today_q = (StoredValueTransaction.query
               .filter(StoredValueTransaction.type == 'topup')
               .filter(StoredValueTransaction.created_at >= today_start_local.astimezone(pytz.utc))
               .filter(StoredValueTransaction.created_at < today_end_local.astimezone(pytz.utc)))
    today_total = sum(t.amount or 0 for t in today_q.all())

    return render_template('wallet_reconcile.html',
                           rows=rows,
                           total_amount=total_amount,
                           count=count,
                           avg_amount=avg_amount,
                           by_remark=by_remark,
                           by_day=by_day,
                           preset=preset,
                           start=start_str,
                           end=end_str,
                           today_total=today_total,
                           start_local_display=(start_local.strftime('%Y-%m-%d')),
                           end_local_display=((end_local - timedelta(days=1)).strftime('%Y-%m-%d')))


def _get_or_create_wallet_by_phone(phone):
    phone = (phone or '').strip()
    wl = Whitelist.query.filter_by(phone=phone).first()
    wallet = StoredValueWallet.query.filter_by(phone=phone).first()
    if not wallet:
        wallet = StoredValueWallet()
        wallet.phone = phone
        wallet.balance = 0
        wallet.whitelist_id = wl.id if wl else None
        db.session.add(wallet)
        db.session.commit()
    return wallet


@admin_bp.route('/wallet/topup', methods=['POST'])
def wallet_topup():
    phone = (request.form.get('phone') or '').strip()
    amount = int(request.form.get('amount') or 0)
    raw_remark = (request.form.get('remark') or '').strip()
    c500 = int(request.form.get('coupon_500_count') or 0)
    c300 = int(request.form.get('coupon_300_count') or 0)
    c100 = int(request.form.get('coupon_100_count') or 0)
    if amount < 0:
        flash('金額不可為負數','warning')
        return redirect(url_for('admin.wallet_home', q=phone))
    wallet = _get_or_create_wallet_by_phone(phone)
    wallet.balance += amount
    wallet.updated_at = datetime.utcnow()
    txn = StoredValueTransaction()
    txn.wallet_id = wallet.id
    txn.type = 'topup'
    txn.amount = amount
    txn.remark = raw_remark if raw_remark else 'TOPUP_CASH'
    txn.coupon_500_count = c500
    txn.coupon_300_count = c300
    try:
        txn.coupon_100_count = c100
    except Exception:
        pass
    db.session.add(txn)
    db.session.commit()
    flash(f'已為 {phone} 儲值 {amount} 元，餘額 {wallet.balance}','success')
    return redirect(url_for('admin.wallet_home', q=phone))


@admin_bp.route('/wallet/consume', methods=['POST'])
def wallet_consume():
    phone = (request.form.get('phone') or '').strip()
    amount = int(request.form.get('amount') or 0)
    raw_remark = (request.form.get('remark') or '').strip()
    c500 = int(request.form.get('coupon_500_count') or 0)
    c300 = int(request.form.get('coupon_300_count') or 0)
    c100 = int(request.form.get('coupon_100_count') or 0)
    wallet = _get_or_create_wallet_by_phone(phone)
    if amount < 0:
        flash('金額不可為負數','warning')
        return redirect(url_for('admin.wallet_home', q=phone))
    if amount > 0 and wallet.balance < amount:
        flash('餘額不足','danger')
        return redirect(url_for('admin.wallet_home', q=phone))
    wallet.balance -= amount
    wallet.updated_at = datetime.utcnow()
    txn = StoredValueTransaction()
    txn.wallet_id = wallet.id
    txn.type = 'consume'
    txn.amount = amount
    txn.remark = raw_remark if raw_remark else 'CONSUME_SERVICE'
    txn.coupon_500_count = c500
    txn.coupon_300_count = c300
    try:
        txn.coupon_100_count = c100
    except Exception:
        pass
    db.session.add(txn)
    db.session.commit()
    flash(f'已為 {phone} 扣款 {amount} 元，餘額 {wallet.balance}','info')
    return redirect(url_for('admin.wallet_home', q=phone))

@admin_bp.route('/wallet/txn/delete', methods=['POST'])
def wallet_txn_delete():
    tid = request.form.get('id')
    q = request.form.get('q') or ''
    if not tid:
        flash('缺少交易 ID','warning')
        return redirect(url_for('admin.wallet_home', q=q))
    t = StoredValueTransaction.query.filter_by(id=tid).first()
    if not t:
        flash('找不到交易紀錄','danger')
        return redirect(url_for('admin.wallet_home', q=q))
    try:
        wallet = StoredValueWallet.query.filter_by(id=t.wallet_id).first()
        # 還原餘額（topup 則扣回，consume 則加回）
        if wallet:
            if t.type == 'topup':
                wallet.balance -= (t.amount or 0)
            elif t.type == 'consume':
                wallet.balance += (t.amount or 0)
            wallet.updated_at = datetime.utcnow()
        db.session.delete(t)
        db.session.commit()
        # 若該錢包已無交易且餘額為 0，刪除錢包紀錄（保持總表乾淨）
        if wallet:
            remain_txn = StoredValueTransaction.query.filter_by(wallet_id=wallet.id).count()
            if remain_txn == 0 and (wallet.balance or 0) == 0:
                db.session.delete(wallet)
                db.session.commit()
        flash('已刪除交易並同步更新餘額','info')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{e}','danger')
    return redirect(url_for('admin.wallet_home', q=q))
