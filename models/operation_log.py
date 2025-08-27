db = None  # 由主程式注入
from datetime import datetime
from models import db

class OperationLog(db.Model):
    __tablename__ = 'operation_log'
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.String(64))
    action = db.Column(db.String(128))
    target_type = db.Column(db.String(32))
    target_id = db.Column(db.Integer)
    detail = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<OperationLog {self.admin} {self.action} {self.target_type} {self.target_id}>'
