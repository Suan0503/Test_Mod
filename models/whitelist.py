from extensions import db

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(32), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
