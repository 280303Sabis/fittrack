from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Rutina

rutinas_bp = Blueprint("rutinas", __name__, url_prefix="/rutinas")


@rutinas_bp.route("/")
@login_required
def lista():
    rutinas = (
        Rutina.query.filter_by(usuario_id=current_user.id)
        .order_by(Rutina.fecha_creacion.desc())
        .all()
    )
    return render_template("rutinas/lista.html", rutinas=rutinas)


@rutinas_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        if not nombre:
            flash("Ponle un nombre a tu rutina.")
            return redirect(url_for("rutinas.nueva"))

        rutina = Rutina(usuario_id=current_user.id, nombre=nombre)
        db.session.add(rutina)
        db.session.commit()

        flash(f"Rutina '{nombre}' creada. Ahora agrégale ejercicios.")
        return redirect(url_for("rutinas.detalle", rutina_id=rutina.id))

    return render_template("rutinas/nueva.html")


@rutinas_bp.route("/<int:rutina_id>")
@login_required
def detalle(rutina_id):
    rutina = Rutina.query.filter_by(id=rutina_id, usuario_id=current_user.id).first_or_404()
    return render_template("rutinas/detalle.html", rutina=rutina)