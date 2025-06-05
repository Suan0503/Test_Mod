from flask import Flask
from extensions import db, line_bot_api, handler, redis_client
from routes.message import message_bp
import os
from dotenv import load_dotenv

# 載入 .env 設定（建議加這一行，讓本地/部署都能自動抓 .env）
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# 註冊 Blueprint
app.register_blueprint(message_bp)

@app.route("/")
def home():
    return "LINE Bot 正常運作中～🍵"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
