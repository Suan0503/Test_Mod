import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Whitelist, Blacklist, TempVerify, StoredValueWallet, StoredValueTransaction, StoredValueCoupon
from utils.db_utils import update_or_create_whitelist_from_data
from hander.verify import EXTRA_NOTICE
from linebot.models import TextSendMessage
from extensions import line_bot_api
from extensions import db
from datetime import datetime
import pytz

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
    # 新：折價券詳細（有期限、無期限、今日抽獎）
    expiring_coupons = []  # list of dict {amount, expiry_date_str, count}
    permanent_coupons = []  # list of dict {amount, count}
    today_draw_coupons = []  # list of dict {amount, count}
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
                # 近期交易（顯示台北時間）
                txns = (StoredValueTransaction.query
                        .filter_by(wallet_id=wallet.id)
                        .order_by(StoredValueTransaction.created_at.desc())
                        .limit(100).all())
                tz = pytz.timezone('Asia/Taipei')
                for t in txns:
                    if t.created_at and t.created_at.tzinfo is None:
                        # assume UTC stored, convert to Taipei for display convenience via a helper
                        t.created_at = t.created_at.replace(tzinfo=pytz.utc).astimezone(tz)
                # 折價券總數（全量計算避免被limit影響）
                all_txns = StoredValueTransaction.query.filter_by(wallet_id=wallet.id).all()
                c500 = c300 = c100 = 0
                for t in all_txns:
                    sign = 1 if t.type == 'topup' else -1
                    c500 += sign * (t.coupon_500_count or 0)
                    c300 += sign * (t.coupon_300_count or 0)
                    c100 += sign * (t.coupon_100_count or 0)
                coupon_500_total = max(c500, 0)
                coupon_300_total = max(c300, 0)
                coupon_100_total = max(c100, 0)
                # 讀取單張折價券
                coupons = StoredValueCoupon.query.filter_by(wallet_id=wallet.id).all()
                tz = pytz.timezone('Asia/Taipei')
                today = datetime.now(tz).date()
                # 分類
                temp_exp_map = {}  # key (amount, expiry_str) -> count
                temp_perm_map = {}  # key amount -> count
                draw_count_map = {}  # amount -> count (today)
                draw_used_map = {}   # amount -> used boolean today
                for c in coupons:
                    expiry_str = None
                    if c.expiry_date:
                        # 將 naive 視為台北時間，不再誤當 UTC 轉換
                        if c.expiry_date.tzinfo:
                            expiry_local = c.expiry_date.astimezone(tz)
                        else:
                            expiry_local = tz.localize(c.expiry_date)
                        expiry_str = expiry_local.strftime('%Y/%m/%d')
                        # 今日抽獎券：source=draw 且 expiry=今日
                        if c.source == 'draw' and expiry_local.date() == today:
                            # 顯示在今日抽獎券（暫存計數，稍後彙總）
                            draw_count_map[c.amount] = draw_count_map.get(c.amount, 0) + 1
                        key = (c.amount, expiry_str)
                        temp_exp_map[key] = temp_exp_map.get(key, 0) + 1
                    else:
                        temp_perm_map[c.amount] = temp_perm_map.get(c.amount, 0) + 1
                # 今日是否使用過抽獎券：從今日 consume 交易看是否有扣除 100/200/300/500
                today_consume = [t for t in txns if t.type == 'consume' and t.created_at.date() == today]
                used_map = {100:0,200:0,300:0,500:0}
                for t in today_consume:
                    used_map[100] += (t.coupon_100_count or 0)
                    used_map[300] += (t.coupon_300_count or 0)
                    used_map[500] += (t.coupon_500_count or 0)
                # 彙總今日抽獎券
                today_draw_coupons = []
                for amt in sorted(draw_count_map.keys()):
                    cnt = draw_count_map[amt]
                    used = used_map.get(amt,0) > 0
                    today_draw_coupons.append({'amount': amt, 'count': cnt, 'used_today': used})
                for (amt, exp_str), cnt in sorted(temp_exp_map.items(), key=lambda x: (x[0][1], x[0][0])):
                    expiring_coupons.append({'amount': amt, 'expiry': exp_str, 'count': cnt})
                for amt, cnt in sorted(temp_perm_map.items()):
                    permanent_coupons.append({'amount': amt, 'count': cnt})
        except Exception as e:
            db.session.rollback()
            error = f"資料讀取錯誤，可能尚未執行遷移：{e}"
    return render_template('wallet.html', q=q, wallet=wallet, txns=txns, error=error,
                           coupon_500_total=coupon_500_total, coupon_300_total=coupon_300_total,
                           coupon_100_total=locals().get('coupon_100_total', 0),
                           expiring_coupons=expiring_coupons, permanent_coupons=permanent_coupons,
                           today_draw_coupons=today_draw_coupons)


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
    expiry_mode = request.form.get('coupon_expiry_mode') or 'expiring'
    expiry_date_raw = request.form.get('coupon_expiry_date') or '2026-01-31'
    expiry_dt = None
    try:
        if expiry_mode == 'expiring':
            expiry_dt = datetime.strptime(expiry_date_raw, '%Y-%m-%d')
    except Exception:
        expiry_dt = None
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
    txn.coupon_100_count = c100
    db.session.add(txn)
    # 建立單張折價券記錄
    def _add_coupons(count, amount):
        for _ in range(count):
            sc = StoredValueCoupon()
            sc.wallet_id = wallet.id
            sc.amount = amount
            sc.expiry_date = expiry_dt if expiry_mode == 'expiring' else None
            sc.source = 'preset' if raw_remark == 'TOPUP_CASH' else 'manual'
            db.session.add(sc)
    _add_coupons(c500, 500)
    _add_coupons(c300, 300)
    _add_coupons(c100, 100)
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
    txn.coupon_100_count = c100
    db.session.add(txn)
    # 扣除單張折價券：依 expiry_date 由最近到期優先，其次無期限
    def _consume_coupons(amount, count):
        if count <= 0:
            return
        q = StoredValueCoupon.query.filter_by(wallet_id=wallet.id, amount=amount).all()
        # 排序：有期限 => 到期日升冪；無期限最後
        q_sorted = sorted(q, key=lambda c: (c.expiry_date is None, c.expiry_date or datetime.max))
        removed = 0
        for c in q_sorted:
            if removed >= count:
                break
            try:
                db.session.delete(c)
                removed += 1
            except Exception:
                pass
    _consume_coupons(500, c500)
    _consume_coupons(300, c300)
    _consume_coupons(100, c100)
    db.session.commit()
    flash(f'已為 {phone} 扣款 {amount} 元，餘額 {wallet.balance}','info')
    return redirect(url_for('admin.wallet_home', q=phone))

@admin_bp.route('/wallet/txn/delete', methods=['POST'])
def wallet_txn_delete():
    tid = request.form.get('id')
    phone = request.form.get('phone')
    txn = StoredValueTransaction.query.filter_by(id=tid).first()
    if not txn:
        flash('找不到該交易','warning')
        return redirect(url_for('admin.wallet_home', q=phone))
    # 調整餘額（若為扣款刪除，需把金額加回；若為儲值刪除，需把金額扣回）
    wallet = StoredValueWallet.query.filter_by(id=txn.wallet_id).first()
    if wallet:
        if txn.type == 'consume':
            wallet.balance += max(txn.amount, 0)
        else:
            wallet.balance -= max(txn.amount, 0)
        wallet.updated_at = datetime.utcnow()
        try:
            db.session.delete(txn)
            db.session.commit()
            flash('交易已刪除並調整餘額','info')
        except Exception as e:
            db.session.rollback()
            flash(f'刪除失敗：{e}','danger')
    return redirect(url_for('admin.wallet_home', q=phone))
