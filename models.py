from flask_login import UserMixin

# 登入用 User 模型
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 角色: admin/user

    def __repr__(self):
        return f'<User {self.username}>'

from extensions import db
from datetime import datetime

class ManualVerifyCode(db.Model):
    __tablename__ = "manual_verify_code"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20), unique=True)
    code = db.Column(db.String(8))
    nickname = db.Column(db.String(255))
    line_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Whitelist(db.Model):
    __tablename__ = "whitelist"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date = db.Column(db.String(20))
    phone = db.Column(db.String(20), unique=True)
    reason = db.Column(db.Text)
    name = db.Column(db.String(255))
    line_id = db.Column(db.String(100))
    line_user_id = db.Column(db.String(255), unique=True)

class Blacklist(db.Model):
    __tablename__ = "blacklist"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date = db.Column(db.String(20))
    phone = db.Column(db.String(20), unique=True)
    reason = db.Column(db.Text)
    name = db.Column(db.String(255))

class Coupon(db.Model):
    __tablename__ = "coupon"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line_user_id = db.Column(db.String(255))
    date = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    report_no = db.Column(db.String(20))  # 新增的流水抽獎券編號
    type = db.Column(db.String(20), default="draw")  # 新增：來源類型 "draw" or "report"
