from extensions import db

class Coupon(db.Model):
    """
    簡易 Coupon model 範例：
    - 用以避免 ImportError，實務可依需求擴充欄位
    """
    __tablename__ = "coupon"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)
    user_identifier = db.Column(db.String(128), nullable=True)
    report_no = db.Column(db.String(64), nullable=True)  # repo 中 report 使用到 report_no
    amount = db.Column(db.Integer, default=0, nullable=False)
    type = db.Column(db.String(32), nullable=True)
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
            "report_no": self.report_no,
            "amount": self.amount,
            "type": self.type,
            "used": self.used,
            "used_at": self.used_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
