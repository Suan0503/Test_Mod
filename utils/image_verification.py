import re
import pytesseract
from PIL import Image, ImageEnhance, ImageOps

def normalize_phone(phone_raw):
    # 去掉空白與 - 和 +號
    phone = re.sub(r"[ \-\+]", "", phone_raw)
    # 若開頭為8869，變成09
    if phone.startswith("8869") and len(phone) == 12:
        phone = "09" + phone[4:]
    # 有些可能缺+，只有886
    elif phone.startswith("886") and len(phone) == 11:
        phone = "09" + phone[3:]
    # 已經是09開頭
    elif phone.startswith("09") and len(phone) == 10:
        pass
    else:
        # 其他不合法格式直接回傳原始
        return phone_raw
    return phone

def detect_platform(image):
    w, h = image.size
    # iOS: 淺色背景，Android: 深色背景
    # 取左上角像素判斷亮度
    px = image.convert('L').getpixel((10, 10))
    if px > 180:
        return 'ios'
    else:
        return 'android'

def preprocess_crop(crop_img):
    gray = ImageOps.grayscale(crop_img)
    enhanced = ImageEnhance.Contrast(gray).enhance(2.0)
    return enhanced

def extract_lineid_phone(image_path, debug=False):
    image = Image.open(image_path)
    w, h = image.size
    platform = detect_platform(image)

    # 根據平台裁切區域
    if platform == 'ios':
        # 手機號碼區域（座標可微調）
        phone_crop = image.crop((50, 500, w-50, 600))
        id_crop = image.crop((50, 650, w-50, 750))
    else:
        # Android 深色背景，區域略下移
        phone_crop = image.crop((50, 500, w-50, 620))
        id_crop = image.crop((50, 700, w-50, 800))

    phone_crop = preprocess_crop(phone_crop)
    id_crop = preprocess_crop(id_crop)

    phone_text = pytesseract.image_to_string(phone_crop, lang='eng+chi_tra')
    id_text = pytesseract.image_to_string(id_crop, lang='eng')

    # 手機號碼正則
    phone_match = re.search(r'((?:\+?886)[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}|09\d{8})', phone_text)
    phone = normalize_phone(phone_match.group(0)) if phone_match else None

    # LINE ID 正則
    lineid_match = re.search(r'([A-Za-z0-9_\-\.]{3,})', id_text)
    lineid = lineid_match.group(1) if lineid_match else None

    if debug:
        print(f"平台: {platform}")
        print("手機區域OCR：", phone_text)
        print("ID區域OCR：", id_text)
        print("手機:", phone)
        print("LINE ID:", lineid)

    # 全文也回傳（方便除錯）
    text = f"[phone_crop]\n{phone_text}\n[id_crop]\n{id_text}"
    return phone, lineid, text

if __name__ == "__main__":
    img_path = input("請輸入圖片路徑：")
    phone, lineid, text = extract_lineid_phone(img_path, debug=True)
    print(f"\n偵測結果：\n手機號碼：{phone or '未識別'}\nLINE ID：{lineid or '未識別'}")
