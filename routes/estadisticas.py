from collections import Counter
from datetime import date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import RegistroActividad

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/estadisticas")

NOMBRES_CATEGORIA = {"pesas": "Pesas / Gimnasio", "crossfit": "Crossfit", "cardio": "Cardio"}


def formato_mm_ss(segundos):
    """Convierte segundos totales a texto 'MM:SS', ej. 125 -> '02:05'."""
    minutos = segundos // 60
    seg_restantes = segundos % 60
    return f"{minutos:02d}:{seg_restantes:02d}"


@estadisticas_bp.route("/")
@login_required
def resumen():
    registros = (
        RegistroActividad.query.filter_by(usuario_id=current_user.id)
        .order_by(RegistroActividad.fecha.desc())
        .all()
    )

    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())

    minutos_semana = sum(
        r.duracion_minutos for r in registros if r.fecha >= inicio_semana
    )

    fechas_con_actividad = {r.fecha for r in registros}
    racha_dias = 0
    dia = hoy
    while dia in fechas_con_actividad:
        racha_dias += 1
        dia -= timedelta(days=1)

    total_sesiones = len(registros)
    ultimos_registros = registros[:5]
    for r in ultimos_registros:
        r.tiempo_exacto = formato_mm_ss(r.duracion_segundos_exactos) if r.duracion_segundos_exactos else None

    dias_semana_es = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    labels_grafica = []
    datos_grafica = []
    for i in range(6, -1, -1):
        fecha_dia = hoy - timedelta(days=i)
        minutos_dia = sum(r.duracion_minutos for r in registros if r.fecha == fecha_dia)
        labels_grafica.append(dias_semana_es[fecha_dia.weekday()])
        datos_grafica.append(minutos_dia)

    # --- Desglose por categoría ---
    # Cada sesión reparte su duración proporcionalmente entre las categorías
    # presentes en su rutina, según cuántos ejercicios tiene de cada una.
    # Ej: rutina con 3 ejercicios de pesas y 1 de cardio -> 75% del tiempo
    # de esa sesión se cuenta como pesas, 25% como cardio.
    minutos_por_categoria = {"pesas": 0.0, "crossfit": 0.0, "cardio": 0.0}
    for r in registros:
        categorias_rutina = [linea.actividad.categoria for linea in r.rutina.actividades]
        if categorias_rutina:
            conteo_categorias = Counter(categorias_rutina)
            total_ejercicios = len(categorias_rutina)
            for cat, cantidad in conteo_categorias.items():
                proporcion = cantidad / total_ejercicios
                minutos_por_categoria[cat] += r.duracion_minutos * proporcion

    total_minutos_categorias = sum(minutos_por_categoria.values())
    desglose_categorias = []
    for cat, minutos in minutos_por_categoria.items():
        porcentaje = round((minutos / total_minutos_categorias) * 100) if total_minutos_categorias else 0
        desglose_categorias.append({
            "nombre": NOMBRES_CATEGORIA[cat],
            "minutos": round(minutos),
            "porcentaje": porcentaje,
        })

    # --- Meta semanal ---
    meta_semanal = current_user.meta_minutos_semana or 150
    progreso_meta = min(100, round((minutos_semana / meta_semanal) * 100)) if meta_semanal else 0

    return render_template(
        "estadisticas/resumen.html",
        minutos_semana=minutos_semana,
        racha_dias=racha_dias,
        total_sesiones=total_sesiones,
        ultimos_registros=ultimos_registros,
        labels_grafica=labels_grafica,
        datos_grafica=datos_grafica,
        desglose_categorias=desglose_categorias,
        meta_semanal=meta_semanal,
        progreso_meta=progreso_meta,
    )


@estadisticas_bp.route("/historial")
@login_required
def historial():
    registros = (
        RegistroActividad.query.filter_by(usuario_id=current_user.id)
        .order_by(RegistroActividad.fecha.desc())
        .all()
    )
    for r in registros:
        r.tiempo_exacto = formato_mm_ss(r.duracion_segundos_exactos) if r.duracion_segundos_exactos else None
    return render_template("estadisticas/historial.html", registros=registros)


@estadisticas_bp.route("/editar/<int:registro_id>", methods=["GET", "POST"])
@login_required
def editar_registro(registro_id):
    registro = RegistroActividad.query.filter_by(id=registro_id, usuario_id=current_user.id).first_or_404()

    if request.method == "POST":
        fecha = request.form.get("fecha")
        duracion_minutos = request.form.get("duracion_minutos")

        if not fecha or not duracion_minutos:
            flash("Completa la fecha y la duración.")
            return redirect(url_for("estadisticas.editar_registro", registro_id=registro.id))

        registro.fecha = fecha
        registro.duracion_minutos = int(duracion_minutos)
        db.session.commit()

        flash("Registro actualizado.")
        return redirect(url_for("estadisticas.historial"))

    return render_template("estadisticas/editar_registro.html", registro=registro)


@estadisticas_bp.route("/eliminar/<int:registro_id>", methods=["POST"])
@login_required
def eliminar_registro(registro_id):
    registro = RegistroActividad.query.filter_by(id=registro_id, usuario_id=current_user.id).first_or_404()

    db.session.delete(registro)
    db.session.commit()

    flash("Registro eliminado.")
    return redirect(url_for("estadisticas.historial"))