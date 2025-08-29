import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # ✅ 確保 handler 可被 import

from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv()

from extensions import db
from routes.message import message_bp
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
# 設定 secret_key，支援 session/flash
import secrets
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# 資料庫連線字串轉換（Heroku/Railway 相容性處理）
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = db.session.query(User).get(session['user_id'])
        if not user or user.role != 'admin':
            flash('只有管理員可操作！')
            return redirect(url_for('schedule'))
        return f(*args, **kwargs)
    return decorated

# Blueprint 註冊

app.register_blueprint(message_bp)

# 取得目前登入者資訊

def get_user_info():
    user = db.session.query(User).get(session.get('user_id'))
    username = user.username if user else None
    group = user.user_group if user else None
    import datetime
    today = datetime.date.today()
    expire_days = None
    if user and user.expire_date:
        expire_days = (user.expire_date.date() - today).days
    return dict(username=username, group=group, expire_days=expire_days)

# 即時班表更新頁面
@app.route("/admin/schedule/")
@login_required
def admin_schedule():
    info = get_user_info()
    return render_template("schedule.html", **info)

# 初始化 admin panel，確保 /admin 路徑可用
from hander.admin_panel import init_admin
with app.app_context():
    db.create_all()
    init_admin(app)

@app.route("/")
@login_required
def home():
    user = db.session.query(User).get(session.get('user_id'))
    import datetime
    today = datetime.date.today()
    expire_days = '未設定'
    group_name = '未知'
    is_superadmin = False
    if user:
        if user.expire_date:
            expire_days = (user.expire_date.date() - today).days
        group_map = {
            'superadmin': '超級管理員',
            'admin': '管理員',
            'switchboard': '總機',
            'operator': '操作人員'
        }
        group_name = group_map.get(user.user_group, '未知')
        is_superadmin = (user.user_group == 'superadmin')
        username = user.username
    else:
        username = '未知'
    return render_template("home.html", username=username, group=group_name, expire_days=expire_days, is_superadmin=is_superadmin)

@app.route('/admin/interface', methods=['GET', 'POST'])
@login_required
def admin_interface():
    info = get_user_info()
    user = db.session.query(User).get(session.get('user_id'))
    if not user or user.user_group != 'superadmin':
        return redirect(url_for('home'))
    msg = None
    if request.method == 'POST':
        target_id = request.form.get('user_id')
        days = int(request.form.get('days', 0))
        target = db.session.query(User).get(target_id)
        if target:
            import datetime
            if target.expire_date and target.expire_date > datetime.datetime.now():
                target.expire_date += datetime.timedelta(days=days)
            else:
                target.expire_date = datetime.datetime.now() + datetime.timedelta(days=days)
            db.session.commit()
            msg = f"已成功為 {target.username} 續費 {days} 天！"
    users = db.session.query(User).all()
    return render_template('admin_interface.html', users=users, msg=msg, **info)

# 搜尋功能
from flask import render_template, request
from models import Whitelist, Blacklist, Coupon

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        # 搜尋白名單
        wl = Whitelist.query.filter(Whitelist.phone.like(f"%{q}%") | Whitelist.name.like(f"%{q}%") | Whitelist.line_id.like(f"%{q}%")).all()
        for w in wl:
            results.append({"type": "白名單", "phone": w.phone, "name": w.name, "line_id": w.line_id})
        # 搜尋黑名單
        bl = Blacklist.query.filter(Blacklist.phone.like(f"%{q}%") | Blacklist.name.like(f"%{q}%")).all()
        for b in bl:
            results.append({"type": "黑名單", "phone": b.phone, "name": b.name})
        # 搜尋抽獎券
        cp = Coupon.query.filter(Coupon.line_user_id.like(f"%{q}%") | Coupon.report_no.like(f"%{q}%")).all()
        for c in cp:
            results.append({"type": "抽獎券", "line_user_id": c.line_user_id, "report_no": c.report_no, "amount": c.amount})
    return render_template("search_result.html", q=q, results=results)

@app.route('/admin/user', methods=['GET'])
@admin_required
def admin_user():
    info = get_user_info()
    users = db.session.query(User).all()
    return render_template('admin_user.html', users=users, **info)

@app.route('/admin/user/delete', methods=['POST'])
@admin_required
def admin_user_delete():
    user_id = request.form['user_id']
    user = db.session.query(User).get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin_user'))

@app.route('/admin/user/role', methods=['POST'])
@admin_required
def admin_user_role():
    user_id = request.form['user_id']
    role = request.form['role']
    user = db.session.query(User).get(user_id)
    if user:
        user.role = role
        db.session.commit()
    return redirect(url_for('admin_user'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            error = '請輸入帳號和密碼'
        elif db.session.query(User).filter_by(username=username).first():
            error = '帳號已存在'
        else:
            pw_hash = generate_password_hash(password)
            # 第一個註冊者自動 admin
            role = 'admin' if db.session.query(User).count() == 0 else 'user'
            user = User(username=username, password_hash=pw_hash, role=role)
            db.session.add(user)
            db.session.commit()
            success = '註冊成功，請登入！'
    return render_template('register.html', error=error, success=success)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = db.session.query(User).filter_by(username=username).first()
        if not user or not check_password_hash(str(user.password_hash), password):
            error = '帳號或密碼錯誤'
        else:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('schedule'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/schedule')
@login_required
def schedule():
    info = get_user_info()
    return render_template('schedule.html', **info)

if __name__ == "__main__":
    # 初始化 admin panel
    from hander.admin_panel import init_admin
    with app.app_context():
        db.create_all()
        init_admin(app)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
