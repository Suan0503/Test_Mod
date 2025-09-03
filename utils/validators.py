import re

def is_valid_phone(text):
    return bool(re.match(r"^09\d{8}$", text))

def is_valid_lineid(text):
    return bool(text and len(text) >= 4)
