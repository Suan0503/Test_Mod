from extensions import db

class CouponModel(db.Model):
    __tablename__ = "coupons"
    id = db.Column(db.Integer, primary_key=True)
    line_user_id = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(32), nullable=False)  # yyyy-mm-dd
    created_at = db.Column(db.DateTime, nullable=False)
