from datetime import datetime
import unicodedata

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.constants import APPOINTMENT_REQUEST_STATUS, APPOINTMENT_SERVICES, DEFAULT_PROFESSIONAL
from app.database import db
from app.models import Appointment
from app.services.input_validation import valid_name, valid_phone


def request_appointment(patient_name, phone, service, preferred_time):
    patient_name = unicodedata.normalize("NFC", patient_name.strip())
    phone = phone.strip()
    service = service.strip()

    if not valid_name(patient_name, 140):
        return False, "Escribe un nombre válido usando letras, espacios, apóstrofes o guiones; no números."
    if not valid_phone(phone):
        return False, "Revisa el teléfono: escribe entre 7 y 15 dígitos; puedes usar +, espacios, paréntesis o guiones."
    if service not in APPOINTMENT_SERVICES:
        return False, "Selecciona uno de los servicios disponibles."

    try:
        appointment_at = datetime.fromisoformat(preferred_time)
    except (TypeError, ValueError):
        return False, "Elige una fecha y hora válida."

    if appointment_at <= datetime.now():
        return False, "Elige una fecha y hora futura para tu solicitud."
    try:
        db.session.add(Appointment(
            patient_name=patient_name,
            phone=phone,
            service=service,
            professional=DEFAULT_PROFESSIONAL,
            appointment_at=appointment_at,
            status=APPOINTMENT_REQUEST_STATUS,
        ))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("No se pudo guardar la solicitud de cita.")
        return False, "No se pudo guardar la solicitud. Revisa la conexión y las tablas de la base de datos."
    return True, "Recibimos tu solicitud. La farmacia se comunicará contigo para confirmar la disponibilidad."
