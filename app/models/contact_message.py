from datetime import datetime

from app.database import db


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    subject = db.Column(db.String(140), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pendiente")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
