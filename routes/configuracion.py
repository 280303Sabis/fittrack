from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user

from extensions import db

configuracion_bp = Blueprint("configuracion", __name__, url_prefix="/configuracion")


@configuracion_bp.route("/", methods=["GET", "POST"])
@login_required
def ver():
    if request.method == "POST":
        meta_minutos_semana = request.form.get("meta_minutos_semana")
        unidad_medida = request.form.get("unidad_medida")

        if not meta_minutos_semana or int(meta_minutos_semana) < 1:
            flash("Indica una meta semanal válida.")
            return redirect(url_for("configuracion.ver"))

        current_user.meta_minutos_semana = int(meta_minutos_semana)
        current_user.unidad_medida = unidad_medida
        db.session.commit()

        flash("Configuración actualizada.")
        return redirect(url_for("configuracion.ver"))

    return render_template("configuracion/ver.html")


@configuracion_bp.route("/cambiar-password", methods=["GET", "POST"])
@login_required
def cambiar_password():
    if request.method == "POST":
        password_actual = request.form.get("password_actual")
        password_nueva = request.form.get("password_nueva")

        if not current_user.check_password(password_actual):
            flash("Tu contraseña actual no es correcta.")
            return redirect(url_for("configuracion.cambiar_password"))

        if not password_nueva:
            flash("Escribe una contraseña nueva.")
            return redirect(url_for("configuracion.cambiar_password"))

        current_user.set_password(password_nueva)
        db.session.commit()

        flash("Tu contraseña fue actualizada.")
        return redirect(url_for("configuracion.ver"))

    return render_template("configuracion/cambiar_password.html")


@configuracion_bp.route("/eliminar-cuenta", methods=["GET", "POST"])
@login_required
def eliminar_cuenta():
    if request.method == "POST":
        password = request.form.get("password")

        if not current_user.check_password(password):
            flash("Tu contraseña no es correcta.")
            return redirect(url_for("configuracion.eliminar_cuenta"))

        usuario = current_user
        logout_user()

        db.session.delete(usuario)
        db.session.commit()

        flash("Tu cuenta y todos tus datos fueron eliminados.")
        return redirect(url_for("home"))

    return render_template("configuracion/eliminar_cuenta.html")