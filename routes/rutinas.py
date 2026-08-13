from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Rutina, Actividad, RutinaActividad, RegistroActividad

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


@rutinas_bp.route("/<int:rutina_id>/agregar/<int:actividad_id>", methods=["GET", "POST"])
@login_required
def agregar_actividad(rutina_id, actividad_id):
    rutina = Rutina.query.filter_by(id=rutina_id, usuario_id=current_user.id).first_or_404()
    actividad = Actividad.query.get_or_404(actividad_id)

    if request.method == "POST":
        series = request.form.get("series")
        repeticiones = request.form.get("repeticiones")
        duracion_minutos = request.form.get("duracion_minutos")

        linea = RutinaActividad(
            rutina_id=rutina.id,
            actividad_id=actividad.id,
            series=int(series) if series else None,
            repeticiones=int(repeticiones) if repeticiones else None,
            duracion_minutos=int(duracion_minutos) if duracion_minutos else None,
            orden=len(rutina.actividades),
        )
        db.session.add(linea)
        db.session.commit()

        flash(f"'{actividad.nombre}' agregado a la rutina.")
        return redirect(url_for("rutinas.detalle", rutina_id=rutina.id))

    return render_template("rutinas/agregar_actividad.html", rutina=rutina, actividad=actividad)


@rutinas_bp.route("/<int:rutina_id>/completar", methods=["GET", "POST"])
@login_required
def completar(rutina_id):
    rutina = Rutina.query.filter_by(id=rutina_id, usuario_id=current_user.id).first_or_404()

    if request.method == "POST":
        duracion_minutos = request.form.get("duracion_minutos")

        if not duracion_minutos:
            flash("Indica cuánto duró tu sesión.")
            return redirect(url_for("rutinas.completar", rutina_id=rutina.id))

        registro = RegistroActividad(
            usuario_id=current_user.id,
            rutina_id=rutina.id,
            duracion_minutos=int(duracion_minutos),
        )
        db.session.add(registro)
        db.session.commit()

        flash(f"¡Rutina '{rutina.nombre}' completada! Buen trabajo.")
        return redirect(url_for("rutinas.detalle", rutina_id=rutina.id))

    return render_template("rutinas/completar.html", rutina=rutina)


@rutinas_bp.route("/<int:rutina_id>/editar/<int:linea_id>", methods=["GET", "POST"])
@login_required
def editar_actividad(rutina_id, linea_id):
    rutina = Rutina.query.filter_by(id=rutina_id, usuario_id=current_user.id).first_or_404()
    linea = RutinaActividad.query.filter_by(id=linea_id, rutina_id=rutina.id).first_or_404()

    if request.method == "POST":
        series = request.form.get("series")
        repeticiones = request.form.get("repeticiones")
        duracion_minutos = request.form.get("duracion_minutos")

        linea.series = int(series) if series else None
        linea.repeticiones = int(repeticiones) if repeticiones else None
        linea.duracion_minutos = int(duracion_minutos) if duracion_minutos else None
        db.session.commit()

        flash(f"'{linea.actividad.nombre}' actualizado.")
        return redirect(url_for("rutinas.detalle", rutina_id=rutina.id))

    return render_template("rutinas/editar_actividad.html", rutina=rutina, linea=linea)


@rutinas_bp.route("/<int:rutina_id>/quitar/<int:linea_id>", methods=["POST"])
@login_required
def quitar_actividad(rutina_id, linea_id):
    rutina = Rutina.query.filter_by(id=rutina_id, usuario_id=current_user.id).first_or_404()
    linea = RutinaActividad.query.filter_by(id=linea_id, rutina_id=rutina.id).first_or_404()

    nombre = linea.actividad.nombre
    db.session.delete(linea)
    db.session.commit()

    flash(f"'{nombre}' se quitó de la rutina.")
    return redirect(url_for("rutinas.detalle", rutina_id=rutina.id))