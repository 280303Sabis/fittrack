from collections import Counter
from datetime import date, timedelta

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import RegistroActividad

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/estadisticas")

NOMBRES_CATEGORIA = {"pesas": "Pesas / Gimnasio", "crossfit": "Crossfit", "cardio": "Cardio"}


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

    dias_semana_es = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    labels_grafica = []
    datos_grafica = []
    for i in range(6, -1, -1):
        fecha_dia = hoy - timedelta(days=i)
        minutos_dia = sum(r.duracion_minutos for r in registros if r.fecha == fecha_dia)
        labels_grafica.append(dias_semana_es[fecha_dia.weekday()])
        datos_grafica.append(minutos_dia)

    # --- Desglose por categoría ---
    # Cada sesión se asigna a la categoría dominante de su rutina
    # (la que más ejercicios tiene), y le sumamos su duración completa.
    minutos_por_categoria = {"pesas": 0, "crossfit": 0, "cardio": 0}
    for r in registros:
        categorias_rutina = [linea.actividad.categoria for linea in r.rutina.actividades]
        if categorias_rutina:
            categoria_dominante = Counter(categorias_rutina).most_common(1)[0][0]
            minutos_por_categoria[categoria_dominante] += r.duracion_minutos

    total_minutos_categorias = sum(minutos_por_categoria.values())
    desglose_categorias = []
    for cat, minutos in minutos_por_categoria.items():
        porcentaje = round((minutos / total_minutos_categorias) * 100) if total_minutos_categorias else 0
        desglose_categorias.append({
            "nombre": NOMBRES_CATEGORIA[cat],
            "minutos": minutos,
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
    return render_template("estadisticas/historial.html", registros=registros)