from linebot.models import MessageEvent, ImageMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction
from extensions import handler, line_bot_api
from utils.image_verification import extract_lineid_phone, normalize_phone
from utils.temp_users import temp_users

import re
from datetime import datetime

RICH_MENU_ID = "你的RichMenuId"  # <- 請換成你系統的 RichMenu ID

def generate_welcome_message(record):
    now_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    return (
        f"📱 {record['phone']}\n"
        f"🌸 暱稱：{record['name']}\n"
        f"       個人編號：{record.get('code','待驗證後產生')}\n"
        f"🔗 LINE ID：{record['line_id']}\n"
        f"🕒 {now_str}\n"
        f"✅ 驗證成功，歡迎加入茗殿\n"
        f"🌟 加入密碼：ming666"
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id
    if user_id not in temp_users or temp_users[user_id].get("step") != "waiting_screenshot":
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    image_path = f"/tmp/{user_id}_line_profile.png"
    with open(image_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    phone_ocr, lineid_ocr, ocr_text = extract_lineid_phone(image_path)
    input_phone = temp_users[user_id].get("phone")
    input_lineid = temp_users[user_id].get("line_id")
    record = temp_users[user_id]

    phone_ocr_norm = normalize_phone(phone_ocr) if phone_ocr else None
    input_phone_norm = normalize_phone(input_phone) if input_phone else None

    # OCR 與手動輸入完全吻合且格式正確才自動通關
    if (
        phone_ocr_norm and lineid_ocr
        and phone_ocr_norm == input_phone_norm
        and input_lineid is not None and lineid_ocr.lower() == input_lineid.lower()
        and re.match(r"^09\d{8}$", phone_ocr_norm)
        and len(lineid_ocr) >= 3 and len(lineid_ocr) <= 20 and re.match(r"^[A-Za-z0-9_\-\.]+$", lineid_ocr)
    ):
        msg = generate_welcome_message(record)
        temp_users.pop(user_id, None)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
        # 開啟主選單
        try:
            line_bot_api.link_rich_menu_to_user(user_id, RICH_MENU_ID)
        except Exception as e:
            print("Set RichMenu failed:", e)
        return

    # LINE ID 尚未設定時，僅允許 phone_ocr 完全正確且格式正確
    if input_lineid == "尚未設定":
        if phone_ocr_norm == input_phone_norm and re.match(r"^09\d{8}$", phone_ocr_norm):
            reply = (
                f"📱 {record['phone']}\n"
                f"🌸 暱稱：{record['name']}\n"
                f"       個人編號：{record.get('code','待驗證後產生')}\n"
                f"🔗 LINE ID：尚未設定\n"
                f"請問以上資料是否正確？正確請回復 1\n"
                f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
            )
            record["step"] = "waiting_confirm"
            temp_users[user_id] = record
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            detect_phone = phone_ocr_norm or '未識別'
            detect_lineid = lineid_ocr or '未識別'
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(
                        text="❌ 截圖中的手機號碼或 LINE ID 與您輸入的不符，請重新上傳正確的 LINE 個人頁面截圖。"
                    ),
                    TextSendMessage(
                        text=f"【圖片偵測結果】\n手機:{detect_phone}\nLINE ID:{detect_lineid}"
                    ),
                    TemplateSendMessage(
                        alt_text="OCR驗證未通過",
                        template=ButtonsTemplate(
                            title="OCR驗證未通過",
                            text="若多次失敗，請申請手動驗證。",
                            actions=[
                                PostbackAction(label="🔔 申請手動驗證", data="manual_verify"),
                            ]
                        )
                    )
                ]
            )
        return

    # 兩者都必須格式正確且完全吻合才能通過
    lineid_match = (lineid_ocr is not None and input_lineid is not None and lineid_ocr.lower() == input_lineid.lower())
    if (
        phone_ocr_norm == input_phone_norm and re.match(r"^09\d{8}$", phone_ocr_norm)
        and (lineid_match or lineid_ocr == "尚未設定")
        and lineid_ocr and len(lineid_ocr) >= 3 and len(lineid_ocr) <= 20 and re.match(r"^[A-Za-z0-9_\-\.]+$", lineid_ocr)
    ):
        reply = (
            f"📱 {record['phone']}\n"
            f"🌸 暱稱：{record['name']}\n"
            f"       個人編號：{record.get('code','待驗證後產生')}\n"
            f"🔗 LINE ID：{record['line_id']}\n"
            f"請問以上資料是否正確？正確請回復 1\n"
            f"⚠️輸入錯誤請從新輸入手機號碼即可⚠️"
        )
        record["step"] = "waiting_confirm"
        temp_users[user_id] = record
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # fallback: OCR 不符，顯示細節
    detect_phone = phone_ocr_norm or '未識別'
    detect_lineid = lineid_ocr or '未識別'
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(
                text="❌ 截圖中的手機號碼或 LINE ID 與您輸入的不符，請重新上傳正確的 LINE 個人頁面截圖。"
            ),
            TextSendMessage(
                text=f"【圖片偵測結果】\n手機:{detect_phone}\nLINE ID:{detect_lineid}"
            ),
            TemplateSendMessage(
                alt_text="OCR驗證未通過",
                template=ButtonsTemplate(
                    title="OCR驗證未通過",
                    text="若多次失敗，請申請手動驗證。",
                    actions=[
                        PostbackAction(label="🔔 申請手動驗證", data="manual_verify"),
                    ]
                )
            )
        ]
    )
