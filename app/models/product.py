
from datetime import date, datetime

from app.database import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(140), nullable=False, index=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    category_ref = db.relationship(
        "Category",
        back_populates="products"
    )

    presentation = db.Column(db.String(80), nullable=False, default="Unidad")
    stock = db.Column(db.Integer, nullable=False, default=0)
    min_stock = db.Column(db.Integer, nullable=False, default=5)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    expiry_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def category(self):
        return self.category_ref.name if self.category_ref else "General"

    @property
    def stock_state(self):
        if self.stock <= 0:
            return "Agotado"
        if self.stock <= self.min_stock:
            return "Por reponer"
        return "Disponible"

    @property
    def expiry_state(self):
        if not self.expiry_date:
            return "Sin fecha"

        days = (self.expiry_date - date.today()).days

        if days < 0:
            return "Vencido"
        if days <= 90:
            return "Próximo a vencer"
        return "Vigente"
