from linebot.models import TextSendMessage
import pytesseract
from PIL import Image
import io

# 驗證流程邏輯

def process_verification(user_id, text, step="phone"):
    if step == "phone":
        # 這裡可加資料庫查詢/暫存
        if text.startswith("09") and len(text) == 10:
            return [TextSendMessage(text="✅ 手機號已登記，請輸入您的 LINE ID")]
        else:
            return [TextSendMessage(text="⚠️ 請輸入有效的手機號碼（09開頭）")]
    elif step == "lineid":
        if text:
            return [TextSendMessage(text="📸 請上傳您的 LINE 個人頁面截圖（需清楚顯示 LINE 名稱與ID）")]
        else:
            return [TextSendMessage(text="⚠️ 請輸入有效的 LINE ID（或輸入：尚未設定）")]
    return [TextSendMessage(text="流程錯誤，請重新開始。")]

def process_ocr_image(event):
    # 這裡僅為範例，實際應取得 image binary
    # image_content = get_image_content(event.message.id)
    # image = Image.open(io.BytesIO(image_content))
    # text = pytesseract.image_to_string(image, lang='chi_tra')
    # return text
    return "（OCR功能尚未串接，僅為範例）"
