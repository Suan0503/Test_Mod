from flask import Flask, request, abort
import os
import psycopg2
from datetime import datetime

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhooks import MessageEvent, FollowEvent, TextMessageContent
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.exceptions import InvalidSignatureError

app = Flask(__name__)

# LINE SDK 設定
channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

# PostgreSQL 連線設定
conn_info = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD")
}

# 簡單暫存使用者輸入的手機號碼（記憶 userId -> phone）
user_phone_map = {}

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK", 200

@handler.add(FollowEvent)
def handle_follow(event):
    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="🎉 歡迎加入～請輸入您的手機號碼進行驗證（只允許一次）")]
            )
        )

@handler.add(MessageEvent)
def handle_message(event):
    if not isinstance(event.message, TextMessageContent):
        return

    user_input = event.message.text.strip()
    user_id = event.source.user_id

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if user_id in user_phone_map and user_input in ["1", "2"]:
            if user_input == "1":
                # 開始進行資料庫驗證流程
                phone = user_phone_map[user_id]
                try:
                    conn = psycopg2.connect(**conn_info)
                    cur = conn.cursor()
                    cur.execute("SELECT status, verified FROM users WHERE phone = %s", (phone,))
                    row = cur.fetchone()

                    if row:
                        status, verified = row
                        if verified:
                            reply = "您已經驗證過囉～"
                        elif status == 'white':
                            cur.execute("UPDATE users SET verified = TRUE WHERE phone = %s", (phone,))
                            reply = "✅ 驗證成功！歡迎您～"
                        elif status == 'black':
                            reply = None
                    else:
                        cur.execute("""
                            INSERT INTO users (phone, status, source, created_at, verified)
                            VALUES (%s, 'white', 'auto-line', %s, TRUE)
                        """, (phone, datetime.now()))
                        reply = "✅ 首次驗證成功，已加入白名單～"

                    conn.commit()
                    cur.close()
                    conn.close()
                    del user_phone_map[user_id]  # 清除暫存

                    if reply:
                        line_bot_api.reply_message(
                            ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply)])
                        )
                    return
                except Exception as e:
                    print("[DB ERROR]", e)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text="🚨 系統忙碌，請稍後再試")])
                    )
                    return

            elif user_input == "2":
                del user_phone_map[user_id]
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text="請重新輸入手機號碼～")])
                )
                return

        # 偵測手機格式
        if user_input.startswith("09") and len(user_input) == 10:
            user_phone_map[user_id] = user_input
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"你輸入的是：{user_input}\n請回覆：1 進行驗證 ✅\n或回覆：2 重新輸入 ❌")]
                )
            )
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="請輸入正確格式的手機號碼（09 開頭共 10 碼）")]
                )
            )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
