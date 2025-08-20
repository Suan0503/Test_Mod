import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from extensions import db
from routes.message import message_bp
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import Whitelist, Blacklist, Coupon  # 若有 Coupon 也可加進來

app = Flask(__name__)

# 資料庫連線字串相容性處理（Heroku/Railway）
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 註冊 LINE Bot 路由
app.register_blueprint(message_bp)

# Flask-Admin 管理後台
class WhitelistAdmin(ModelView):
    can_edit = True
    can_create = True
    can_delete = True

class BlacklistAdmin(ModelView):
    can_edit = True
    can_create = True
    can_delete = True

class CouponAdmin(ModelView):
    can_edit = True
    can_create = True
    can_delete = True

admin = Admin(app, name='資料庫管理後台', template_mode='bootstrap4')
admin.add_view(WhitelistAdmin(Whitelist, db.session, name='白名單'))
admin.add_view(BlacklistAdmin(Blacklist, db.session, name='黑名單'))
admin.add_view(CouponAdmin(Coupon, db.session, name='折價券'))  # 若要管理 coupon

@app.route("/")
def home():
    try:
        db.session.execute("SELECT 1")
        db_status = "資料庫連線正常"
    except Exception as e:
        db_status = "資料庫連線異常: " + str(e)
    return f"LINE Bot 正常運作中～🍵<br>{db_status}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
