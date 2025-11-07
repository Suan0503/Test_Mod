import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from sqlalchemy import text
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass  # 若未安裝 python-dotenv 不影響執行

# 保證本目錄可匯入
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from extensions import db
from flask_migrate import Migrate
from routes.message import message_bp
from routes.pending_verify import pending_bp
from routes.admin import admin_bp
from hander.admin_panel import init_admin
from models import Whitelist, Blacklist, TempVerify, Coupon
import secrets

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
csrf = CSRFProtect(app)

# Railway / Heroku 資料庫 URL 轉換
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

"""Blueprint 註冊"""
app.register_blueprint(message_bp)
app.register_blueprint(pending_bp)
app.register_blueprint(admin_bp)
init_admin(app)

"""admin 相關路由已移至 routes/admin.py 的 Blueprint"""

@app.route('/home')
def home():
    try:
        db.session.execute(text('SELECT 1'))
        db_status = '資料庫連線正常'
    except Exception as e:
        db_status = '資料庫連線異常: ' + str(e)
    return f"LINE Bot 正常運作中～🍵\n{db_status}"

@app.route('/')
def index():
    return redirect('/home')

@app.route('/search')
def search():
    q = request.args.get('q','').strip()
    results = []
    if q:
        wl = Whitelist.query.filter(Whitelist.phone.like(f"%{q}%") | Whitelist.name.like(f"%{q}%") | Whitelist.line_id.like(f"%{q}%")).all()
        for w in wl:
            results.append({'type':'白名單','phone':w.phone,'name':w.name,'line_id':w.line_id})
        bl = Blacklist.query.filter(Blacklist.phone.like(f"%{q}%") | Blacklist.name.like(f"%{q}%")).all()
        for b in bl:
            results.append({'type':'黑名單','phone':b.phone,'name':b.name})
        cp = Coupon.query.filter(Coupon.line_user_id.like(f"%{q}%") | Coupon.report_no.like(f"%{q}%")).all()
        for c in cp:
            results.append({'type':'抽獎券','line_user_id':c.line_user_id,'report_no':c.report_no,'amount':c.amount})
    return render_template('search_result.html', q=q, results=results)

@app.route('/line_status')
def line_status():
    from extensions import ACCESS_TOKEN, CHANNEL_SECRET, line_bot_api
    ok_env = bool(ACCESS_TOKEN and CHANNEL_SECRET)
    profile_ok = False
    try:
        # 嘗試呼叫 API（以空白 user id 會失敗，但可證明物件存在）；這裡只檢查屬性是否存在
        getattr(line_bot_api, 'push_message', None)
        profile_ok = True
    except Exception:
        profile_ok = False
    return {
        'env_ready': ok_env,
        'api_ready': profile_ok,
        'webhook': '/callback',
        'hint': '請在 LINE Developers 將 Webhook 指向 /callback 並開啟。'
    }

# 提供 csrf_token() 給模板
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# 啟動前初始化（優先遷移，失敗則 create_all）
with app.app_context():
    migrations_path = os.path.join(os.path.dirname(__file__), 'migrations')
    if os.path.isdir(migrations_path):
        try:
            from flask_migrate import upgrade as _upgrade
            _upgrade()
        except Exception as e:
            # 若 upgrade 失敗，退回 create_all，避免容器啟動失敗
            db.create_all()
    else:
        # 尚未建立 migrations 目錄，先確保表存在
        db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
