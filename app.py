from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

from extensions import db
from routes.message import message_bp
from models import CouponModel  # 確保 models 初始化

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.register_blueprint(message_bp)

@app.route("/")
def home():
    return "LINE Bot 正常運作中～🍵"

if __name__ == "__main__":
    # 初次部署時可用這行建立資料表
    # with app.app_context():
    #     db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
