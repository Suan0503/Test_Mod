"""
Coupon 資料模型
"""
from extensions import db
from datetime import datetime

class Coupon(db.Model):
    __tablename__ = "coupon"
    id = db.Column(db.Integer, primary_key=True)
    line_user_id = db.Column(db.String(255))
    date = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    report_no = db.Column(db.String(20))  # 流水抽獎券編號
    type = db.Column(db.String(20), default="draw")  # 來源類型 "draw" or "report"
