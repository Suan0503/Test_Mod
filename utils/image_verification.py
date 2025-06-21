import re
from paddleocr import PaddleOCR
import cv2
import numpy as np

# 初始化 PaddleOCR（建議單例，避免重複初始化）
ocr_model = PaddleOCR(use_angle_cls=True, lang='ch')

def extract_lineid_phone(image_path):
    # 讀取圖片
    img = cv2.imread(image_path)
    # 執行 OCR
    result = ocr_model.ocr(img, cls=True)
    # 將辨識結果組合成一串文字
    text = ''
    for line in result:
        for word_info in line:
            text += word_info[1][0] + '\n'

    # 手機號碼正則
    phone_match = re.search(r'((?:\+?886)[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}|09\d{8})', text)
    phone = phone_match.group(0) if phone_match else None
    lineid_match = re.search(r'ID[\s:：]{0,2}([A-Za-z0-9_\-\.]{3,})', text, re.IGNORECASE)
    lineid = lineid_match.group(1) if lineid_match else None

    return phone, lineid, text
