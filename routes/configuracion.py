import csv
import io

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user, logout_user

from extensions import db
from models import RegistroActividad
from utils import password_es_segura

configuracion_bp = Blueprint("configuracion", __name__, url_prefix="/configuracion")


@configuracion_bp.route("/", methods=["GET", "POST"])
@login_required
def ver():
    if request.method == "POST":
        tipo_meta = request.form.get("tipo_meta")
        meta_minutos_semana = request.form.get("meta_minutos_semana")
        meta_dias_semana = request.form.get("meta_dias_semana")
        unidad_medida = request.form.get("unidad_medida")

        if tipo_meta == "dias":
            if not meta_dias_semana or int(meta_dias_semana) < 1 or int(meta_dias_semana) > 7:
                flash("Indica una meta de días válida (entre 1 y 7).")
                return redirect(url_for("configuracion.ver"))
            current_user.meta_dias_semana = int(meta_dias_semana)
        else:
            if not meta_minutos_semana or int(meta_minutos_semana) < 1:
                flash("Indica una meta semanal válida.")
                return redirect(url_for("configuracion.ver"))
            current_user.meta_minutos_semana = int(meta_minutos_semana)

        current_user.tipo_meta = tipo_meta
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

        es_segura, mensaje_error = password_es_segura(password_nueva)
        if not es_segura:
            flash(mensaje_error)
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

@configuracion_bp.route("/exportar-datos")
@login_required
def exportar_datos():
    registros = (
        RegistroActividad.query.filter_by(usuario_id=current_user.id)
        .order_by(RegistroActividad.fecha.desc())
        .all()
    )

    salida = io.StringIO()
    escritor = csv.writer(salida)

    # Sección 1: datos de perfil
    escritor.writerow(["--- PERFIL ---"])
    escritor.writerow(["Nombre", "Correo", "Peso (kg)", "Altura (cm)", "Edad", "Objetivo", "Meta semanal (min)"])
    escritor.writerow([
        current_user.nombre, current_user.email, current_user.peso_kg,
        current_user.altura_cm, current_user.edad, current_user.objetivo,
        current_user.meta_minutos_semana,
    ])
    escritor.writerow([])

    # Sección 2: historial de sesiones
    escritor.writerow(["--- HISTORIAL DE ACTIVIDAD ---"])
    escritor.writerow(["Rutina", "Fecha", "Duración (min)"])
    for r in registros:
        escritor.writerow([r.rutina.nombre, r.fecha.strftime("%d/%m/%Y"), r.duracion_minutos])

    salida.seek(0)
    contenido = "\ufeff" + salida.getvalue()  # BOM: le dice a Excel que el archivo es UTF-8
    return Response(
        contenido,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=fittrack_mis_datos.csv"},
    )