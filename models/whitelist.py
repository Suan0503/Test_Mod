from extensions import db

class Whitelist(db.Model):
    __tablename__ = "whitelist"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    line_id = db.Column(db.String(100), nullable=True)
    line_user_id = db.Column(db.String(100), unique=True, nullable=True)
    reason = db.Column(db.String(255), nullable=True)
    date = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
