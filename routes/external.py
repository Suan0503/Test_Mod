from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import ExternalUser, FeatureFlag
from werkzeug.security import generate_password_hash, check_password_hash

external_bp = Blueprint('external', __name__, url_prefix='/MT_System')

@external_bp.route('/')
def external_home():
    return redirect(url_for('external.external_login'))

@external_bp.route('/login', methods=['GET','POST'])
def external_login():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = (request.form.get('password') or '').strip()
        user = ExternalUser.query.filter_by(email=email, is_active=True).first()
        if user and check_password_hash(user.password_hash, password):
            session['ext_user_id'] = user.id
            return redirect(url_for('external.features'))
        flash('登入失敗','danger')
    return render_template('external_login.html')

@external_bp.route('/register', methods=['GET','POST'])
def external_register():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = (request.form.get('password') or '').strip()
        if not email or not password:
            flash('缺少必要欄位','warning')
            return redirect(url_for('external.external_register'))
        exists = ExternalUser.query.filter_by(email=email).first()
        if exists:
            flash('Email 已被註冊','danger')
            return redirect(url_for('external.external_register'))
        u = ExternalUser()
        u.email = email
        u.password_hash = generate_password_hash(password)
        u.is_active = True
        db.session.add(u)
        db.session.commit()
        flash('註冊成功，請登入','success')
        return redirect(url_for('external.external_login'))
    return render_template('external_register.html')

def _require_ext_login():
    uid = session.get('ext_user_id')
    if not uid:
        return False
    return True

@external_bp.route('/features', methods=['GET','POST'])
def features():
    if not _require_ext_login():
        return redirect(url_for('external.external_login'))
    if request.method == 'POST':
        # 簡易開關（示範）：根據提交的鍵更新 enabled。付費流程另接第三方。
        for f in FeatureFlag.query.all():
            enabled = request.form.get(f'flag_{f.key}') == 'on'
            f.enabled = enabled
        db.session.commit()
        flash('已更新功能開關','success')
    flags = FeatureFlag.query.order_by(FeatureFlag.name.asc()).all()
    return render_template('external_features.html', flags=flags)

@external_bp.route('/logout')
def external_logout():
    session.pop('ext_user_id', None)
    flash('已登出','info')
    return redirect(url_for('external.external_login'))

@external_bp.route('/seed')
def external_seed():
    """一次性種子：需提供 ?token= 與環境變數 SEED_TOKEN 相同，建立外部使用者與預設功能旗標。
    安全建議：完成後請移除 SEED_TOKEN 或停用此路由。
    """
    import os
    token = (request.args.get('token') or '').strip()
    expected = os.getenv('SEED_TOKEN', '')
    if not expected or token != expected:
        flash('未授權','danger')
        return redirect(url_for('external.external_login'))
    # 建立外部使用者（若不存在）
    admin_email = os.getenv('SEED_ADMIN_EMAIL', 'admin@example.com')
    admin_pass = os.getenv('SEED_ADMIN_PASSWORD', 'change-me')
    user = ExternalUser.query.filter_by(email=admin_email).first()
    if not user:
        user = ExternalUser()
        user.email = admin_email
        user.password_hash = generate_password_hash(admin_pass)
        user.is_active = True
        db.session.add(user)
    # 預置功能旗標
    defaults = [
        ('verify_flow', '驗證流程', '外部可使用基本驗證功能'),
        ('wallet_reporting', '錢包報表', '查詢報表與摘要'),
        ('csv_export', '匯出功能', 'CSV/JSON 匯出'),
        ('line_tools', 'LINE 工具', 'LINE 相關工具'),
    ]
    for key, name, desc in defaults:
        ff = FeatureFlag.query.filter_by(key=key).first()
        if not ff:
            ff = FeatureFlag()
            ff.key = key
            ff.name = name
            ff.description = desc
            ff.enabled = False
            db.session.add(ff)
    db.session.commit()
    flash('種子資料已建立','success')
    return redirect(url_for('external.external_login'))
