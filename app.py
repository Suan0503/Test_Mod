import os
from flask import Flask
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

from extensions import db
from routes.message import message_bp

# 建立 Flask app
app = Flask(__name__)

# 取得並正規化 DATABASE_URL（支援 Heroku/Railway）
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 初始化 SQLAlchemy
db.init_app(app)

# 註冊 Blueprint
app.register_blueprint(message_bp)

# 健康檢查路由
@app.route("/")
def home():
    try:
        db.session.execute("SELECT 1")
        db_status = "資料庫連線正常"
    except Exception as e:
        db_status = "資料庫連線異常: " + str(e)
    return f"LINE Bot 正常運作中～🍵\n{db_status}"

if __name__ == "__main__":
    # 支援 Railway/Heroku 指定 PORT
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
