from flask import Blueprint, request, abort, jsonify
from extensions import line_bot_api, handler, db
from linebot.models import (
    MessageEvent, TextMessage, FlexSendMessage, FollowEvent, ImageMessage, TextSendMessage
)
from linebot.exceptions import InvalidSignatureError
from datetime import datetime
import pytz
import os
import re
import random
import string
import traceback
from threading import Thread

from models import Whitelist, Blacklist, Coupon
from utils.draw_utils import draw_coupon, get_today_coupon_flex, has_drawn_today, save_coupon_record
from utils.image_verification import extract_lineid_phone
from utils.special_case import is_special_case

message_bp = Blueprint('message', __name__)

ADMIN_IDS = [
    "U2bcd63000805da076721eb62872bc39f",
    "U5ce6c382d12eaea28d98f2d48673b4b8",
    "U8f3cc921a9dd18d3e257008a34dd07c1",
]

temp_users = {}
manual_verify_pending = {}

def generate_verify_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def choose_link():
    group = [
        "https://line.me/ti/p/g7TPO_lhAL",
        "https://line.me/ti/p/Q6-jrvhXbH",
        "https://line.me/ti/p/AKRUvSCLRC"
    ]
    return group[hash(os.urandom(8)) % len(group)]

def get_function_menu_flex():
    return FlexSendMessage(
        alt_text="功能選單",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": "✨ 功能選單 ✨", "weight": "bold", "size": "lg", "align": "center", "color": "#C97CFD"},
                    {"type": "separator"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "📱 驗證資訊", "text": "驗證資訊"},
                                "style": "primary",
                                "color": "#FFB6B6"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "📅 每日班表",
                                    "uri": "https://t.me/+LaFZixvTaMY3ODA1"
                                },
                                "style": "secondary",
                                "color": "#FFF8B7"
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "🎁 每日抽獎", "text": "每日抽獎"},
                                "style": "primary",
                                "color": "#A3DEE6"
                            },
                            {
                                "type": "button",
                                "action": {"type": "uri", "label": "📬 預約諮詢", "uri": choose_link()},
                                "style": "primary",
                                "color": "#B889F2"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "🌸 茗殿討論區",
                                    "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
                                },
                                "style": "primary",
                                "color": "#FFDCFF"
                            }
                        ]
                    }
                ]
            }
        }
    )

def update_or_create_whitelist_from_data(data, user_id=None):
    existing = Whitelist.query.filter_by(phone=data["phone"]).first()
    need_commit = False
    if existing:
        if data.get("name") and (not existing.name):
            existing.name = data["name"]
            need_commit = True
        if data.get("line_id") and (not existing.line_id):
            existing.line_id = data["line_id"]
            need_commit = True
        if user_id and (not existing.line_user_id):
            existing.line_user_id = user_id
            need_commit = True
        if data.get("reason") and (not existing.reason):
            existing.reason = data["reason"]
            need_commit = True
        if data.get("date") and (not existing.date):
            existing.date = data["date"]
            need_commit = True
        if need_commit:
            db.session.commit()
        return existing, False
    else:
        new_user = Whitelist(
            phone=data["phone"],
            name=data.get("name"),
            line_id=data.get("line_id"),
            line_user_id=user_id if user_id else data.get("line_user_id"),
            reason=data.get("reason"),
            date=data.get("date"),
            created_at=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user, True

@message_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("❗ callback 發生例外：", e)
        traceback.print_exc()
        abort(500)
    return "OK"

@handler.add(FollowEvent)
def handle_follow(event):
    msg = (
        "歡迎加入🍵茗殿🍵\n"
        "請正確按照步驟提供資料配合快速驗證\n\n"
        "➡️ 請輸入手機號碼進行驗證（含09開頭）"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 你的原始 handle_message 內容這裡照常貼，略…
    # 因內容過長，請直接複製你原本的
    pass

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id
    if user_id not in temp_users or temp_users[user_id].get("step") != "waiting_screenshot":
        return

    # 先回覆，避免 LINE 499 超時
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="圖片收到，正在辨識，結果會稍後推播給您！")
    )

    def ocr_and_push():
        try:
            message_content = line_bot_api.get_message_content(event.message.id)
            image_path = f"/tmp/{user_id}_line_profile.png"
            with open(image_path, 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)

            phone_ocr, lineid_ocr, ocr_text = extract_lineid_phone(image_path)
            input_phone = temp_users[user_id].get("phone")
            input_lineid = temp_users[user_id].get("line_id")
            record = temp_users[user_id]

            if is_special_case(user_id):
                reply = (
                    f"📱 {record['phone']}\n"
                    f"🌸 暱稱：{record['name']}\n"
                    f"       個人編號：待驗證後產生\n"
                    f"🔗 LINE ID：{record['line_id']}\n"
                    f"（此用戶經手動通過）\n"
                    f"請問以上資料是否正確？正確請回復 1\n"
                    f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
                )
                record["step"] = "waiting_confirm"
                temp_users[user_id] = record
                line_bot_api.push_message(user_id, TextSendMessage(text=reply))
                return

            if input_lineid == "尚未設定":
                if phone_ocr == input_phone:
                    reply = (
                        f"📱 {record['phone']}\n"
                        f"🌸 暱稱：{record['name']}\n"
                        f"       個人編號：待驗證後產生\n"
                        f"🔗 LINE ID：尚未設定\n"
                        f"請問以上資料是否正確？正確請回復 1\n"
                        f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
                    )
                    record["step"] = "waiting_confirm"
                    temp_users[user_id] = record
                    line_bot_api.push_message(user_id, TextSendMessage(text=reply))
                else:
                    line_bot_api.push_message(
                        user_id,
                        TextSendMessage(text="❌ 截圖中的手機號碼與您輸入的不符，請重新上傳正確的 LINE 個人頁面截圖。")
                    )
            else:
                lineid_match = (lineid_ocr is not None and input_lineid is not None and lineid_ocr.lower() == input_lineid.lower())
                if phone_ocr == input_phone and (lineid_match or lineid_ocr == "尚未設定"):
                    reply = (
                        f"📱 {record['phone']}\n"
                        f"🌸 暱稱：{record['name']}\n"
                        f"       個人編號：待驗證後產生\n"
                        f"🔗 LINE ID：{record['line_id']}\n"
                        f"請問以上資料是否正確？正確請回復 1\n"
                        f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
                    )
                    record["step"] = "waiting_confirm"
                    temp_users[user_id] = record
                    line_bot_api.push_message(user_id, TextSendMessage(text=reply))
                else:
                    line_bot_api.push_message(
                        user_id,
                        TextSendMessage(
                            text=(
                                "❌ 截圖中的手機號碼或 LINE ID 與您輸入的不符，請重新上傳正確的 LINE 個人頁面截圖。\n"
                                f"【圖片偵測結果】手機:{phone_ocr or '未識別'}\nLINE ID:{lineid_ocr or '未識別'}"
                            )
                        )
                    )
        except Exception as e:
            line_bot_api.push_message(
                user_id,
                TextSendMessage(text=f"❗ 圖片辨識過程發生錯誤，請稍後再試。錯誤訊息：{str(e)}")
            )

    Thread(target=ocr_and_push).start()

@message_bp.route("/ocr", methods=["POST"])
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
