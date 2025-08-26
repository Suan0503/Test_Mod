from extensions import db

class Coupon(db.Model):
    """
    最小的 Coupon model 範例
    - code: 優惠券代碼（可唯一）
    - user_identifier: 綁定的使用者 identifier（例如 LINE userId / email / phone）
    - used: 是否已被使用
    - used_at: 使用時間（若已使用）
    """
    __tablename__ = "coupon"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)
    user_identifier = db.Column(db.String(128), nullable=True)
    used = db.Column(db.Boolean, default=False, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    def __repr__(self):
        return f"<Coupon id={self.id} code={self.code} user={self.user_identifier} used={self.used}>"

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "user_identifier": self.user_identifier,
            "used": self.used,
            "used_at": self.used_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
