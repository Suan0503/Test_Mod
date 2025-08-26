from extensions import db

class Whitelist(db.Model):
    __tablename__ = "whitelist"
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(128), unique=True, nullable=False)  # e.g. LINE userId or phone/email
    name = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    note = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "identifier": self.identifier,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "note": self.note,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
