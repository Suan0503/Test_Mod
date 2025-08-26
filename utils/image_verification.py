"""
圖片 OCR 驗證工具
"""
import re
import pytesseract
from PIL import Image

def normalize_phone(phone_raw):
    phone = re.sub(r"[ \-\+]", "", phone_raw)
    if phone.startswith("8869") and len(phone) == 12:
        phone = "09" + phone[4:]
    elif phone.startswith("886") and len(phone) == 11:
        phone = "09" + phone[3:]
    elif phone.startswith("09") and len(phone) == 10:
        pass
    else:
        return phone_raw
    return phone

def extract_lineid_phone(image_path, debug=False):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='eng+chi_tra')
    phone_match = re.search(r'((?:\+?886)[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}|09\d{8})', text)
    phone = normalize_phone(phone_match.group(0)) if phone_match else None
    lineid_match = re.search(r'ID[\s:\uff1a]{0,2}([A-Za-z0-9_\-\.]{3,})', text, re.IGNORECASE)
    lineid = lineid_match.group(1) if lineid_match else None
    if debug:
        print("OCR全文:\n", text)
        print("手機:", phone)
        print("LINE ID:", lineid)
    return phone, lineid, text

if __name__ == "__main__":
    img_path = input("請輸入圖片路徑：")
    phone, lineid, text = extract_lineid_phone(img_path, debug=True)
    print(f"\n偵測結果：\n手機號碼：{phone or '未識別'}\nLINE ID：{lineid or '未識別'}")
