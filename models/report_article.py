from extensions import db
from datetime import datetime

class ReportArticle(db.Model):
    __tablename__ = "report_article"
    id = db.Column(db.Integer, primary_key=True)
    line_user_id = db.Column(db.String(255))
    nickname = db.Column(db.String(255))
    member_id = db.Column(db.Integer)
    line_id = db.Column(db.String(100))
    url = db.Column(db.String(512))
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.String(255))
    ticket_code = db.Column(db.String(20))
    reject_reason = db.Column(db.Text)
