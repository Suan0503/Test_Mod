import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # 確保 handler 可被 import

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from extensions import db
from routes.blacklist import blacklist_bp
from routes.whitelist import whitelist_bp
from routes.dashboard import dashboard_bp
from routes.message import message_bp  # 如果有 LINE webhook 路由

app = Flask(__name__)

# 資料庫連線字串轉換（Heroku/Railway 相容性處理）
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Blueprint 註冊
app.register_blueprint(blacklist_bp, url_prefix="/blacklist")
app.register_blueprint(whitelist_bp, url_prefix="/whitelist")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(message_bp)  # 如果有 LINE webhook

@app.route("/")
def home():
    try:
        db.session.execute("SELECT 1")
        db_status = "資料庫連線正常"
    except Exception as e:
        db_status = "資料庫連線異常: " + str(e)
    return f"管理員後台正常運作中～🍵\n{db_status}\n請使用功能列進行操作"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
