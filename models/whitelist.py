from extensions import db

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    note = db.Column(db.String(256), nullable=True)
