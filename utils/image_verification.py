import re
from paddleocr import PaddleOCR
import cv2

# 只初始化一次，放在全域
ocr_model = PaddleOCR(use_angle_cls=True, lang='ch')

def extract_lineid_phone(image_path):
    img = cv2.imread(image_path)
    result = ocr_model.ocr(img)  # 不要加 cls 參數！

    # 合併辨識結果成一串文字
    text = ''
    if result:
        for line in result:
            for word_info in line:
                text += word_info[1][0] + '\n'

    # 手機號碼正則
    phone_match = re.search(r'((?:\+?886)[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}|09\d{8})', text)
    phone = phone_match.group(0) if phone_match else None

    # LINE ID 正則
    lineid_match = re.search(r'ID[\s:：]{0,2}([A-Za-z0-9_\-\.]{3,})', text, re.IGNORECASE)
    lineid = lineid_match.group(1) if lineid_match else None

    return phone, lineid, text
