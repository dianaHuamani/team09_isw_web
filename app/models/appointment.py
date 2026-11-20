from datetime import datetime

from app.database import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(140), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    professional = db.Column(db.String(100), nullable=False, default="Por asignar")
    appointment_at = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="Programada")
    notes = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
