from extensions import db

class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    reason = db.Column(db.String(256), nullable=True)
