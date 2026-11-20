import re
import unicodedata

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.models import ContactMessage
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
from app.services.input_validation import valid_name, valid_phone


def submit_contact_message(name, email, phone, subject, message):
    name = unicodedata.normalize("NFC", name.strip())
    email = email.strip()
    phone = phone.strip()
    subject = subject.strip()
    message = message.strip()

    if not all([name, email, subject, message]):
        return False, "Completa los campos obligatorios para enviar tu mensaje."
    if not valid_name(name, 120):
        return False, "Escribe un nombre válido usando letras, espacios, apóstrofes o guiones; no números."
    if len(email) > 160 or not EMAIL_PATTERN.fullmatch(email):
        return False, "Escribe un correo electrónico válido."
    if phone and not valid_phone(phone):
        return False, "Revisa el teléfono: escribe entre 7 y 15 dígitos; puedes usar +, espacios, paréntesis o guiones."
    if len(subject) > 140 or len(message) < 10 or len(message) > 4000:
        return False, "El asunto debe tener hasta 140 caracteres y el mensaje entre 10 y 4000."

    entry = ContactMessage(
        name=name,
        email=email,
        phone=phone or None,
        subject=subject,
        message=message,
    )
    try:
        db.session.add(entry)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("No se pudo guardar el mensaje de contacto en la base de datos.")
        return False, "No se pudo guardar el mensaje. Revisa la conexión RDS, el nombre de la base y la tabla contact_messages."
    return True, "Gracias por escribirnos. Recibimos tu mensaje."
