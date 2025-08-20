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

# 首頁路由：電話查詢
@app.route("/", methods=["GET", "POST"])
def home():
    search_result = None
    phone = ""
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        whitelist = db.session.query(Whitelist).filter_by(phone=phone).first()
        blacklist = db.session.query(Blacklist).filter_by(phone=phone).first()
        search_result = {
            "phone": phone,
            "whitelist": whitelist,
            "blacklist": blacklist,
        }
    # 用 render_template_string 快速產生 HTML
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
        {% if search_result.whitelist %}
            <div style="color:green;">
                <b>白名單</b>：{{ search_result.whitelist.name }}（{{ search_result.whitelist.phone }}）
                {% if search_result.whitelist.line_id %}，LINE ID: {{ search_result.whitelist.line_id }}{% endif %}
                {% if search_result.whitelist.reason %}<br>原因：{{ search_result.whitelist.reason }}{% endif %}
            </div>
        {% endif %}
        {% if search_result.blacklist %}
            <div style="color:red;">
                <b>黑名單</b>：{{ search_result.blacklist.name }}（{{ search_result.blacklist.phone }}）
                {% if search_result.blacklist.reason %}<br>原因：{{ search_result.blacklist.reason }}{% endif %}
            </div>
        {% endif %}
        {% if not search_result.whitelist and not search_result.blacklist %}
            <div style="color:gray;">查無此電話於白/黑名單。</div>
        {% endif %}
    {% endif %}
    """, search_result=search_result, phone=phone)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
