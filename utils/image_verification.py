from paddleocr import PaddleOCR
import cv2
import re
import numpy as np

ocr_model = PaddleOCR(use_angle_cls=True, lang='ch')

def extract_lineid_phone(image_path):
    img = cv2.imread(image_path)
    result = ocr_model.ocr(img)  # 注意：不要再加 cls 參數！

    text = ''
    for line in result:
        for word_info in line:
            text += word_info[1][0] + '\n'

    phone_match = re.search(r'((?:\+?886)[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}|09\d{8})', text)
    phone = phone_match.group(0) if phone_match else None
    lineid_match = re.search(r'ID[\s:：]{0,2}([A-Za-z0-9_\-\.]{3,})', text, re.IGNORECASE)
    lineid = lineid_match.group(1) if lineid_match else None

    return phone, lineid, text
