from datetime import date

from pathlib import Path

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request,
    send_from_directory, session, url_for
)
from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.models import Category, Product

from app.constants import APPOINTMENT_SERVICES
from app.services.appointment_service import request_appointment
from app.services.catalog_service import list_public_categories, list_public_products
from app.services.contact_service import submit_contact_message

bp = Blueprint("main", __name__)


@bp.route("/sitemap.xml")
def sitemap():
    project_root = Path(current_app.root_path).parent
    return send_from_directory(project_root, "sitemap.xml", mimetype="application/xml")


@bp.app_context_processor
def inject_today():
    return {"today": date.today()}


@bp.route("/")
def dashboard():
    return render_template("home.html", products=list_public_products(limit=6))


@bp.route("/productos")
def inventory():
    search = request.args.get("q", "").strip()
    category = request.args.get("categoria", "").strip()
    return render_template(
        "products.html",
        products=list_public_products(search=search, category=category),
        categories=list_public_categories(),
        search=search,
        category=category,
    )


@bp.route("/citas", methods=["GET", "POST"])
def appointments():
    if request.method == "POST":
        success, message = request_appointment(
            request.form.get("patient_name", ""),
            request.form.get("phone", ""),
            request.form.get("service", ""),
            request.form.get("appointment_at", ""),
        )
        flash(message, "success" if success else "error")
        if success:
            return redirect(url_for("main.appointments"))
    return render_template("appointments.html", services=APPOINTMENT_SERVICES)


@bp.route("/contacto", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        success, message = submit_contact_message(
            request.form.get("name", ""),
            request.form.get("email", ""),
            request.form.get("phone", ""),
            request.form.get("subject", ""),
            request.form.get("message", ""),
        )
        flash(message, "success" if success else "error")
        if success:
            return redirect(url_for("main.contacts"))
    return render_template("contacts.html")


def admin_required():
    return session.get("is_admin") is True


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        configured_password = current_app.config.get("ADMIN_PASSWORD", "")
        if (
            configured_password
            and username == current_app.config.get("ADMIN_USERNAME")
            and password == configured_password
        ):
            session.clear()
            session["is_admin"] = True
            flash("Sesión administrativa iniciada.", "success")
            return redirect(url_for("main.admin_products"))
        flash("Usuario o contraseña incorrectos. Verifica ADMIN_USERNAME y ADMIN_PASSWORD.", "error")
    return render_template("admin_login.html")


@bp.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("main.admin_login"))


@bp.route("/admin/productos")
def admin_products():
    if not admin_required():
        return redirect(url_for("main.admin_login"))
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin_products.html", products=products)


@bp.route("/admin/productos/nuevo", methods=["GET", "POST"])
def admin_product_new():
    if not admin_required():
        return redirect(url_for("main.admin_login"))
    categories = Category.query.order_by(Category.name).all()
    if request.method == "POST":
        try:
            category = db.session.get(Category, int(request.form.get("category_id", "0")))
            sku = request.form.get("sku", "").strip()
            name = request.form.get("name", "").strip()
            presentation = request.form.get("presentation", "").strip()
            stock = int(request.form.get("stock", "0"))
            min_stock = int(request.form.get("min_stock", "0"))
            price = float(request.form.get("price", "0"))
            expiry_raw = request.form.get("expiry_date", "").strip()
            expiry_date = date.fromisoformat(expiry_raw) if expiry_raw else None
            if not category or not sku or not name or not presentation:
                raise ValueError("Completa todos los campos obligatorios.")
            if stock < 0 or min_stock < 0 or price < 0:
                raise ValueError("Stock, stock mínimo y precio no pueden ser negativos.")
            product = Product(
                sku=sku, name=name, category_id=category.id,
                presentation=presentation, stock=stock,
                min_stock=min_stock, price=price, expiry_date=expiry_date,
            )
            db.session.add(product)
            db.session.commit()
            flash("Medicamento registrado correctamente.", "success")
            return redirect(url_for("main.admin_products"))
        except (ValueError, TypeError):
            db.session.rollback()
            flash("Revisa los datos: categoría, cantidades, precio y fecha deben ser válidos.", "error")
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("No se pudo registrar el producto.")
            flash("No se pudo registrar. Comprueba el SKU y la conexión a RDS.", "error")
    return render_template("admin_product_form.html", product=None, categories=categories)


@bp.route("/admin/productos/<int:product_id>/editar", methods=["GET", "POST"])
def admin_product_edit(product_id):
    if not admin_required():
        return redirect(url_for("main.admin_login"))
    product = db.get_or_404(Product, product_id)
    categories = Category.query.order_by(Category.name).all()
    if request.method == "POST":
        try:
            category = db.session.get(Category, int(request.form.get("category_id", "0")))
            stock = int(request.form.get("stock", "0"))
            min_stock = int(request.form.get("min_stock", "0"))
            price = float(request.form.get("price", "0"))
            expiry_raw = request.form.get("expiry_date", "").strip()
            if not category or stock < 0 or min_stock < 0 or price < 0:
                raise ValueError("Datos no válidos.")
            product.sku = request.form.get("sku", "").strip()
            product.name = request.form.get("name", "").strip()
            product.category_id = category.id
            product.presentation = request.form.get("presentation", "").strip()
            product.stock = stock
            product.min_stock = min_stock
            product.price = price
            product.expiry_date = date.fromisoformat(expiry_raw) if expiry_raw else None
            if not product.sku or not product.name or not product.presentation:
                raise ValueError("Completa los campos obligatorios.")
            db.session.commit()
            flash("Medicamento actualizado correctamente.", "success")
            return redirect(url_for("main.admin_products"))
        except (ValueError, TypeError):
            db.session.rollback()
            flash("Revisa los datos ingresados.", "error")
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("No se pudo actualizar el producto.")
            flash("No se pudo actualizar el medicamento.", "error")
    return render_template("admin_product_form.html", product=product, categories=categories)


@bp.route("/admin/productos/<int:product_id>/eliminar", methods=["POST"])
def admin_product_delete(product_id):
    if not admin_required():
        return redirect(url_for("main.admin_login"))
    product = db.get_or_404(Product, product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash("Medicamento eliminado correctamente.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("No se pudo eliminar el producto.")
        flash("No se pudo eliminar el medicamento.", "error")
    return redirect(url_for("main.admin_products"))
