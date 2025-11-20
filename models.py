from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class TempVerify(db.Model):
    __tablename__ = "temp_verify"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20))
    line_id = db.Column(db.String(100))
    nickname = db.Column(db.String(255))
    line_user_id = db.Column(db.String(255))
    status = db.Column(db.String(20), default="pending")  # pending/verified/failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


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


# 儲值金錢包
class StoredValueWallet(db.Model):
    __tablename__ = "stored_value_wallet"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 對應白名單使用者（非強制外鍵，避免跨 DB 差異）
    whitelist_id = db.Column(db.Integer, index=True)
    phone = db.Column(db.String(20), index=True)
    balance = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 每日到期提醒用
    last_coupon_notice_at = db.Column(db.DateTime)


# 儲值金交易紀錄
class StoredValueTransaction(db.Model):
    __tablename__ = "stored_value_txn"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wallet_id = db.Column(db.Integer, index=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # topup / consume
    amount = db.Column(db.Integer, nullable=False)
    remark = db.Column(db.Text)  # 例如預約記錄
    coupon_500_count = db.Column(db.Integer, default=0, nullable=False)
    coupon_300_count = db.Column(db.Integer, default=0, nullable=False)
    # 新增 100 券
    coupon_100_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# ===== 公開網站：使用者、班表、回報文/作品、媒體 =====
class SiteUser(db.Model):
    __tablename__ = 'site_user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        try:
            return check_password_hash(self.password_hash, password)
        except Exception:
            return False


class MediaAsset(db.Model):
    __tablename__ = 'media_asset'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), nullable=False)  # S3/Cloudflare R2 或本地 /static/uploads
    key = db.Column(db.String(512))  # 供 S3 刪除使用
    filename = db.Column(db.String(255))
    content_type = db.Column(db.String(120))
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class ScheduleEntry(db.Model):
    __tablename__ = 'schedule_entry'
    id = db.Column(db.Integer, primary_key=True)
    girl_name = db.Column(db.String(120), index=True, nullable=False)
    nation = db.Column(db.String(10))  # tw/vn/th/id
    room = db.Column(db.String(50))
    start_time = db.Column(db.DateTime, index=True, nullable=False)
    duration_min = db.Column(db.Integer, nullable=False)  # 40/60/90
    languages = db.Column(db.String(50))  # 以逗號分隔 zh,en
    price = db.Column(db.Integer)
    visible = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, index=True)  # SiteUser.id
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Post(db.Model):
    __tablename__ = 'site_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text)
    cover_asset_id = db.Column(db.Integer, index=True)
    price = db.Column(db.Integer)
    is_published = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

