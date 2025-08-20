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
from models import Whitelist, Blacklist

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(message_bp)

# 加入 Flask-Admin 後台
admin = Admin(app, name='資料庫管理後台', template_mode='bootstrap4')
admin.add_view(ModelView(Whitelist, db.session, name='白名單'))
admin.add_view(ModelView(Blacklist, db.session, name='黑名單'))

@app.route("/")
def home():
    try:
        db.session.execute("SELECT 1")
        db_status = "資料庫連線正常"
    except Exception as e:
        db_status = "資料庫連線異常: " + str(e)
    return f"LINE Bot 正常運作中～🍵\n{db_status}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
