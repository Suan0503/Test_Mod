import re
import pytesseract
from PIL import Image

def normalize_phone(phone_raw):
    if not phone_raw:
        return None
    # 去除空白、-、+號
    phone = re.sub(r"[ \-\+]", "", phone_raw)
    # 台灣手機號處理
    if phone.startswith("8869") and len(phone) == 12:
        phone = "09" + phone[4:]
    elif phone.startswith("886") and len(phone) == 11:
        phone = "09" + phone[3:]
    elif phone.startswith("09") and len(phone) == 10:
        pass
    else:
        # 其他狀況直接回傳原樣
        return phone_raw
    return phone

def extract_lineid_phone(image_path, debug=False):
    try:
        image = Image.open(image_path)
    except Exception as e:
        if debug:
            print(f"無法開啟圖片: {e}")
        return None, None, ""

    # 只用英文和繁體中文辨識
    try:
        text = pytesseract.image_to_string(image, lang='eng+chi_tra')
    except Exception as e:
        if debug:
            print(f"OCR辨識失敗: {e}")
        return None, None, ""

    # 手機號正則 (台灣號碼)
    phone_regex = r"(09\d{8}|8869\d{8}|\+8869\d{8})"
    phone_match = re.search(phone_regex, text.replace(" ", "").replace("-", ""))
    phone = normalize_phone(phone_match.group(0)) if phone_match else None

    # LINE ID 正則
    # 支援 ID: abc123 / ID：abc123 / Id: abc123 / ID abc123 / IDabc123
    lineid_regex = r"(?:ID|Id|id)[\s:：\-]*([A-Za-z0-9_\-\.]{3,})"
    lineid_match = re.search(lineid_regex, text)
    lineid = lineid_match.group(1) if lineid_match else None

    if debug:
        print("====== OCR全文 ======")
        print(text)
        print("====== 手機號 ======")
        print(phone or "未識別")
        print("====== LINE ID ======")
        print(lineid or "未識別")

    return phone, lineid, text
