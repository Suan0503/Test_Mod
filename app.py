import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # ✅ 確保 handler 可被 import

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from extensions import db
from routes.message import message_bp

# 匯入新增的 list_admin blueprint
from routes.list_admin import list_admin_bp

app = Flask(__name__)

# 基本設定
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-to-secure-key")
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///test_mod.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Blueprint 註冊
app.register_blueprint(message_bp)
app.register_blueprint(list_admin_bp)  # 名單管理

@app.route("/")
def home():
    try:
        db.session.execute("SELECT 1")
        db_status = "資料庫連線正常"
    except Exception as e:
        db_status = "資料庫連線異常: " + str(e)
    return f"LINE Bot 正常運作中～🍵\n{db_status}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
