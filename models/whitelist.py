from extensions import db
from datetime import datetime

class Whitelist(db.Model):
    __tablename__ = "whitelist"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 新增 / 調整欄位以配合 routes/templates 的使用
    identifier = db.Column(db.String(255), unique=True, nullable=True)  # e.g. LINE userId / phone / email
    date = db.Column(db.String(20))
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(255))
    note = db.Column(db.Text)
    reason = db.Column(db.Text)
    name = db.Column(db.String(255))
    line_id = db.Column(db.String(100))
    line_user_id = db.Column(db.String(255), unique=True)
