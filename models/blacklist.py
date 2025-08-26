"""
Blacklist 資料模型
"""
from extensions import db
from datetime import datetime

class Blacklist(db.Model):
    __tablename__ = "blacklist"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    identifier = db.Column(db.String(255), unique=True, nullable=True)
    date = db.Column(db.String(20))
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(255))
    reason = db.Column(db.Text)
    note = db.Column(db.Text)
    name = db.Column(db.String(255))
