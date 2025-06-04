from flask import Blueprint
from extensions import db
from models import Whitelist
from services.redis_util import set_temp_user, get_temp_user, del_temp_user, set_manual_pending, get_manual_pending, del_manual_pending
import random, string, pytz
from datetime import datetime
from linebot.models import TextSendMessage

admin_bp = Blueprint('admin', __name__)

ADMIN_IDS = [
    "U2bcd63000805da076721eb62872bc39f",
    "U5ce6c382d12eaea28d98f2d48673b4b8",
]

def generate_verify_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def handle_manual_verify(event, user_text, user_id, line_bot_api, profile):
    tz = pytz.timezone("Asia/Taipei")
    # ... 直接把你 main.py 內手動驗證流程搬過來並改成 redis 版本
    # 詳細流程參考前面提供的 admin blueprint code
    # 回傳 True 表示這裡流程已經攔截
    ...
