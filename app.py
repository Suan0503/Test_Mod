import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # ✅ 確保 handler 可被 import

from flask import Flask
from config import config

from extensions import db, migrate
from routes.message import message_bp

# 匯入新增的 list_admin blueprint
from routes.list_admin import list_admin_bp

# 匯入 sqlalchemy.text 用於安全執行文字 SQL
from sqlalchemy import text

def create_app(config_name=None):
    """Application factory function."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 設定 logging
    logging.basicConfig(level=app.config['LOG_LEVEL'])
    logger = logging.getLogger(__name__)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
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
            logger.exception("資料庫連線檢查發生錯誤")
            db_status = "資料庫連線異常: " + str(e)
        return f"LINE Bot 正常運作中～🍵\n{db_status}"
    
    return app

# Create app instance
app = create_app()
logger = logging.getLogger(__name__)

# 如果需要在啟動時建立表（僅在你明確設定 INIT_DB=1 時執行）
if os.environ.get("INIT_DB", "0") == "1":
    try:
        with app.app_context():
            logger.info("INIT_DB=1 -> 執行 db.create_all() 建立缺少的表格（不會修改既有欄位）")
            db.create_all()
            logger.info("db.create_all() 執行完成")
    except Exception:
        logger.exception("執行 db.create_all() 時發生錯誤")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    logger.info(f"Starting Flask app on 0.0.0.0:{port} (debug={debug})")
    # 如果你用 docker / railway，PORT 會由環境提供
    app.run(host="0.0.0.0", port=port, debug=debug)
