import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Whitelist, Blacklist, TempVerify
from extensions import db

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


@admin_bp.route('/')
def admin_root():
    return redirect(url_for('admin.home'))

@admin_bp.route('/home')
def home():
    whitelists, blacklists, tempverifies = load_dashboard_data()
    return render_template('admin_home.html', whitelists=whitelists, blacklists=blacklists, tempverifies=tempverifies, limit=DASHBOARD_LIMIT)


@admin_bp.route('/dashboard')
def admin_dashboard():
    return render_dashboard()


# 白名單
@admin_bp.route('/whitelist/search')
def whitelist_search():
    q = request.args.get('q', '').strip()
    if q:
        whitelists = Whitelist.query.filter(
            Whitelist.phone.like(f"%{q}%") |
            Whitelist.name.like(f"%{q}%") |
            Whitelist.line_id.like(f"%{q}%")
        ).order_by(Whitelist.created_at.desc()).limit(DASHBOARD_LIMIT).all()
    else:
        whitelists = None
    return render_dashboard(whitelists=whitelists)


@admin_bp.route('/whitelist/add', methods=['POST'])
def whitelist_add():
    phone = request.form.get('phone','').strip()
    name = request.form.get('name','').strip()
    line_id = request.form.get('line_id','').strip()
    if not phone or not name or not line_id:
        flash('白名單新增資料不完整','warning')
        return redirect(url_for('admin.admin_dashboard'))
    if Whitelist.query.filter_by(phone=phone).first():
        flash('手機已存在於白名單','danger')
        return redirect(url_for('admin.admin_dashboard'))
    w = Whitelist(phone=phone, name=name, line_id=line_id)
    db.session.add(w)
    db.session.commit()
    flash('白名單新增成功','success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/whitelist/delete', methods=['POST'])
def whitelist_delete():
    phone = request.form.get('phone','').strip()
    w = Whitelist.query.filter_by(phone=phone).first()
    if not w:
        flash('找不到該白名單紀錄','danger')
        return redirect(url_for('admin.admin_dashboard'))
    db.session.delete(w)
    db.session.commit()
    flash('白名單刪除成功','info')
    return redirect(url_for('admin.admin_dashboard'))


# 黑名單
@admin_bp.route('/blacklist/search')
def blacklist_search():
    q = request.args.get('q','').strip()
    if q:
        blacklists = Blacklist.query.filter(
            Blacklist.phone.like(f"%{q}%") |
            Blacklist.name.like(f"%{q}%")
        ).order_by(Blacklist.created_at.desc()).limit(DASHBOARD_LIMIT).all()
    else:
        blacklists = None
    return render_dashboard(blacklists=blacklists)


@admin_bp.route('/blacklist/add', methods=['POST'])
def blacklist_add():
    phone = request.form.get('phone','').strip()
    name = request.form.get('name','').strip()
    reason = request.form.get('reason','').strip()
    if not phone or not name or not reason:
        flash('黑名單新增資料不完整','warning')
        return redirect(url_for('admin.admin_dashboard'))
    if Blacklist.query.filter_by(phone=phone).first():
        flash('手機已存在於黑名單','danger')
        return redirect(url_for('admin.admin_dashboard'))
    b = Blacklist(phone=phone, name=name, reason=reason)
    db.session.add(b)
    db.session.commit()
    flash('黑名單新增成功','success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/blacklist/delete', methods=['POST'])
def blacklist_delete():
    phone = request.form.get('phone','').strip()
    b = Blacklist.query.filter_by(phone=phone).first()
    if not b:
        flash('找不到該黑名單紀錄','danger')
        return redirect(url_for('admin.admin_dashboard'))
    db.session.delete(b)
    db.session.commit()
    flash('黑名單刪除成功','info')
    return redirect(url_for('admin.admin_dashboard'))


# 暫存名單（待驗證）
@admin_bp.route('/tempverify/verify', methods=['POST'])
def tempverify_verify():
    _id = request.form.get('id')
    tv = TempVerify.query.filter_by(id=_id).first()
    if not tv:
        flash('找不到暫存名單','danger')
        return redirect(url_for('admin.admin_dashboard'))
    tv.status = 'verified'
    db.session.commit()
    flash('暫存名單標記為通過，請視需要同步至白名單','success')
    return redirect(url_for('admin.admin_dashboard'))


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
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/schedule/')
def admin_schedule():
    return render_template('schedule.html')
