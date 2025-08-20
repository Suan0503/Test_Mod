import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

from extensions import db
from routes.message import message_bp
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import Whitelist, Blacklist

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(message_bp)

# 只查詢，不允許新增/編輯/刪除
class ReadOnlyModelView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    page_size = 50
    def is_accessible(self):
        return True

admin = Admin(app, name='茗殿專用查詢系統', template_mode='bootstrap4')
admin.add_view(ReadOnlyModelView(Whitelist, db.session, name='白名單'))
admin.add_view(ReadOnlyModelView(Blacklist, db.session, name='黑名單'))

# 主頁查詢（自訂模板）
@app.route("/", methods=["GET", "POST"])
def home():
    search_result = []
    phone = ""
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        query_phones = [phone]
        if len(phone) == 9 and not phone.startswith("0"):
            query_phones.append("0" + phone)
        for p in query_phones:
            whitelist = db.session.query(Whitelist).filter_by(phone=p).first()
            blacklist = db.session.query(Blacklist).filter_by(phone=p).first()
            if whitelist:
                search_result.append({"type": "white", "phone": p, "record": whitelist})
            if blacklist:
                search_result.append({"type": "black", "phone": p, "record": blacklist})
    return render_template("search.html", search_result=search_result, phone=phone)

@app.route("/db_status")
def db_status():
    try:
        db.session.execute("SELECT 1")
        db_status = "資料庫連線正常"
    except Exception as e:
        db_status = "資料庫連線異常: " + str(e)
    return f"LINE Bot 正常運作中～🍵<br>{db_status}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
