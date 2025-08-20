import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, render_template_string, request
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
    # 隱藏 "Create"、"Edit"、"Delete" 相關按鈕
    def is_accessible(self):
        return True

admin = Admin(app, name='茗殿專用查詢系統', template_mode='bootstrap4')
admin.add_view(ReadOnlyModelView(Whitelist, db.session, name='白名單'))
admin.add_view(ReadOnlyModelView(Blacklist, db.session, name='黑名單'))
# 不加 Coupon，所以不會出現折價券

# 首頁路由：電話查詢（自動補0查詢9碼和10碼）
@app.route("/", methods=["GET", "POST"])
def home():
    search_result = []
    phone = ""
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        query_phones = [phone]
        # 如果是9碼且第一碼不是0，自動加0組成10碼
        if len(phone) == 9 and not phone.startswith("0"):
            query_phones.append("0" + phone)

        # 查詢黑白名單
        for p in query_phones:
            whitelist = db.session.query(Whitelist).filter_by(phone=p).first()
            blacklist = db.session.query(Blacklist).filter_by(phone=p).first()
            if whitelist:
                search_result.append({
                    "type": "white",
                    "phone": p,
                    "record": whitelist
                })
            if blacklist:
                search_result.append({
                    "type": "black",
                    "phone": p,
                    "record": blacklist
                })

    return render_template_string("""
    <h2>茗殿專用查詢系統</h2>
    <form method="post">
        <label for="phone">請輸入電話：</label>
        <input type="text" name="phone" id="phone" value="{{ phone }}" placeholder="例如 0912345678">
        <button type="submit">查詢</button>
    </form>
    {% if search_result %}
        <hr>
        <h4>查詢結果</h4>
        {% for result in search_result %}
            {% if result.type == 'white' %}
                <div style="color:green;">
                    <b>白名單</b>：{{ result.record.name }}（{{ result.record.phone }}）
                    {% if result.record.line_id %}，LINE ID: {{ result.record.line_id }}{% endif %}
                    {% if result.record.reason %}<br>原因：{{ result.record.reason }}{% endif %}
                </div>
            {% elif result.type == 'black' %}
                <div style="color:red;">
                    <b>黑名單</b>：{{ result.record.name }}（{{ result.record.phone }}）
                    {% if result.record.reason %}<br>原因：{{ result.record.reason }}{% endif %}
                </div>
            {% endif %}
        {% endfor %}
        {% if not search_result %}
            <div style="color:gray;">查無此電話於白/黑名單。</div>
        {% endif %}
    {% endif %}
    """, search_result=search_result, phone=phone)

# 保留原本的 Flask-Admin 後台查詢功能
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
