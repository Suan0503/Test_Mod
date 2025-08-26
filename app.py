"""
主程式入口
"""
import sys
import os
import logging
<<<<<<< HEAD
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
=======
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # ✅ 確保 handler 可被 import

>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
from flask import Flask
from dotenv import load_dotenv
load_dotenv()
from extensions import db
from routes.message import message_bp
<<<<<<< HEAD
from routes.list_admin import list_admin_bp
from sqlalchemy import text
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
app = Flask(__name__)
=======

# 匯入新增的 list_admin blueprint
from routes.list_admin import list_admin_bp

# 匯入 sqlalchemy.text 用於安全執行文字 SQL
from sqlalchemy import text

# 設定 logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 基本設定
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-to-secure-key")
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///test_mod.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
<<<<<<< HEAD
if os.environ.get("INIT_DB", "0") == "1":
    try:
        with app.app_context():
            logger.info("INIT_DB=1 -> 執行 db.create_all() 建立缺少的表格(不會修改既有欄位)")
=======

# 如果需要在啟動時建立表（僅在你明確設定 INIT_DB=1 時執行）
if os.environ.get("INIT_DB", "0") == "1":
    try:
        with app.app_context():
            logger.info("INIT_DB=1 -> 執行 db.create_all() 建立缺少的表格（不會修改既有欄位）")
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
            db.create_all()
            logger.info("db.create_all() 執行完成")
    except Exception:
        logger.exception("執行 db.create_all() 時發生錯誤")
<<<<<<< HEAD
app.register_blueprint(message_bp)
app.register_blueprint(list_admin_bp)
@app.route("/")
def home():
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "資料庫連線正常"
    except Exception as e:
=======

# Blueprint 註冊
app.register_blueprint(message_bp)
app.register_blueprint(list_admin_bp)  # 名單管理

@app.route("/")
def home():
    try:
        # SQLAlchemy 要求文字 SQL 明確使用 text()
        db.session.execute(text("SELECT 1"))
        db_status = "資料庫連線正常"
    except Exception as e:
        # 記錄完整錯誤到 log，以便在部署平台查看
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
        logger.exception("資料庫連線檢查發生錯誤")
        db_status = "資料庫連線異常: " + str(e)
    return f"LINE Bot 正常運作中～\n{db_status}"
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    logger.info(f"Starting Flask app on 0.0.0.0:{port} (debug={debug})")
<<<<<<< HEAD
=======
    # 如果你用 docker / railway，PORT 會由環境提供
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
    app.run(host="0.0.0.0", port=port, debug=debug)
