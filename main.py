from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, FollowEvent, ImageMessage
)
from linebot.exceptions import InvalidSignatureError
from datetime import datetime
from dotenv import load_dotenv
import os
import re
import traceback
import pytz
import random
import string

from draw_utils import draw_coupon, get_today_coupon_flex, has_drawn_today, save_coupon_record
from image_verification import extract_lineid_phone
from special_case import is_special_case

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

ADMIN_IDS = [
    "U2bcd63000805da076721eb62872bc39f",
    "U5ce6c382d12eaea28d98f2d48673b4b8",
]

temp_users = {}
manual_verify_pending = {}

def generate_verify_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date = db.Column(db.String(20))
    phone = db.Column(db.String(20), unique=True)
    reason = db.Column(db.Text)
    name = db.Column(db.String(255))
    line_id = db.Column(db.String(100))
    line_user_id = db.Column(db.String(255), unique=True)

class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date = db.Column(db.String(20))
    phone = db.Column(db.String(20), unique=True)
    reason = db.Column(db.Text)
    name = db.Column(db.String(255))

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    line_user_id = db.Column(db.String(255))
    date = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

def choose_link():
    group = [
        "https://line.me/ti/p/g7TPO_lhAL",
        "https://line.me/ti/p/Q6-jrvhXbH",
        "https://line.me/ti/p/AKRUvSCLRC"
    ]
    return group[hash(os.urandom(8)) % len(group)]

@app.route("/")
def home():
    return "LINE Bot 正常運作中～🍵"

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("❗ webhook 發生例外：", e)
        traceback.print_exc()
        abort(500)
    return "OK"

@app.route("/ocr", methods=["POST"])
def ocr_image_verification():
    if "image" not in request.files:
        return jsonify({"error": "請上傳圖片（欄位名稱 image）"}), 400
    file = request.files["image"]
    file_path = "temp_ocr_img.png"
    file.save(file_path)
    phone, line_id, text = extract_lineid_phone(file_path)
    os.remove(file_path)
    return jsonify({
        "phone": phone,
        "line_id": line_id,
        "ocr_text": text
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
