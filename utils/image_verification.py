import re
import pytesseract
from PIL import Image

def extract_lineid_phone(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='eng+chi_tra')
    phone_match = re.search(r'((?:\+?886)[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}|09\d{8})', text)
    phone = phone_match.group(0) if phone_match else None
    lineid_match = re.search(r'ID[\s:：]{0,2}([A-Za-z0-9_\-\.]{3,})', text, re.IGNORECASE)
    lineid = lineid_match.group(1) if lineid_match else None
    return phone, lineid, text
