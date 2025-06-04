from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# 載入 .env 設定
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Blueprint 註冊
from routes.message import message_bp
app.register_blueprint(message_bp)

@app.route("/")
def home():
    return "LINE Bot 正常運作中～🍵"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
