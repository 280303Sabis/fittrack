from collections import Counter
from datetime import date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import RegistroActividad, Rutina

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

    # Sesiones completadas esta semana (para la meta por días)
    sesiones_semana = len({r.fecha for r in registros if r.fecha >= inicio_semana})

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
    # Si la sesión viene del cronómetro, ya sabemos el tiempo REAL de cada
    # ejercicio (guardado en RegistroActividadDetalle) y lo usamos directo.
    # Si viene de "Marcar como completada" a mano, no hay ese detalle, así
    # que repartimos el tiempo total proporcionalmente entre las categorías
    # presentes en la rutina (mismo cálculo estimado de antes).
    minutos_por_categoria = {"pesas": 0.0, "crossfit": 0.0, "cardio": 0.0}
    for r in registros:
        if r.detalles:
            for detalle in r.detalles:
                categoria = detalle.rutina_actividad.actividad.categoria
                minutos_por_categoria[categoria] += detalle.duracion_segundos / 60
        else:
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
    # Puede ser en minutos o en días entrenados, según lo que el usuario
    # haya elegido en Configuración.
    tipo_meta = current_user.tipo_meta or "minutos"
    if tipo_meta == "dias":
        meta_semanal = current_user.meta_dias_semana or 5
        progreso_actual = sesiones_semana
        progreso_meta = min(100, round((progreso_actual / meta_semanal) * 100)) if meta_semanal else 0
    else:
        meta_semanal = current_user.meta_minutos_semana or 150
        progreso_actual = minutos_semana
        progreso_meta = min(100, round((progreso_actual / meta_semanal) * 100)) if meta_semanal else 0

    return render_template(
        "estadisticas/resumen.html",
        minutos_semana=minutos_semana,
        racha_dias=racha_dias,
        total_sesiones=total_sesiones,
        ultimos_registros=ultimos_registros,
        labels_grafica=labels_grafica,
        datos_grafica=datos_grafica,
        desglose_categorias=desglose_categorias,
        tipo_meta=tipo_meta,
        meta_semanal=meta_semanal,
        progreso_actual=progreso_actual,
        progreso_meta=progreso_meta,
    )


@estadisticas_bp.route("/historial")
@login_required
def historial():
    busqueda = request.args.get("q", "").strip()
    pagina = request.args.get("pagina", 1, type=int)
    por_pagina = 10

    query = (
        RegistroActividad.query
        .join(Rutina)
        .filter(RegistroActividad.usuario_id == current_user.id)
    )

    if busqueda:
        query = query.filter(Rutina.nombre.ilike(f"%{busqueda}%"))

    query = query.order_by(RegistroActividad.fecha.desc())

    total_registros = query.count()
    total_paginas = max(1, (total_registros + por_pagina - 1) // por_pagina)
    pagina = max(1, min(pagina, total_paginas))

    registros = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()

    for r in registros:
        r.tiempo_exacto = formato_mm_ss(r.duracion_segundos_exactos) if r.duracion_segundos_exactos else None
        r.detalle_display = [
            {"nombre": d.rutina_actividad.actividad.nombre, "tiempo": formato_mm_ss(d.duracion_segundos)}
            for d in r.detalles
        ]

    return render_template(
        "estadisticas/historial.html",
        registros=registros,
        busqueda=busqueda,
        pagina=pagina,
        total_paginas=total_paginas,
        total_registros=total_registros,
    )


@estadisticas_bp.route("/editar/<int:registro_id>", methods=["GET", "POST"])
@login_required
def editar_registro(registro_id):
    registro = RegistroActividad.query.filter_by(id=registro_id, usuario_id=current_user.id).first_or_404()

    if request.method == "POST":
        fecha = request.form.get("fecha")

        if not fecha:
            flash("Indica la fecha.")
            return redirect(url_for("estadisticas.editar_registro", registro_id=registro.id))

        registro.fecha = fecha

        if registro.detalles:
            # Sesión con detalle por ejercicio: la duración total se
            # recalcula sola, sumando el tiempo de cada ejercicio.
            for detalle in registro.detalles:
                campo_min = f"detalle_{detalle.id}_min"
                campo_seg = f"detalle_{detalle.id}_seg"
                minutos_detalle = request.form.get(campo_min)
                segundos_detalle = request.form.get(campo_seg)
                if minutos_detalle is not None and segundos_detalle is not None:
                    detalle.duracion_segundos = int(minutos_detalle) * 60 + int(segundos_detalle)

            total_segundos = sum(d.duracion_segundos for d in registro.detalles)
            registro.duracion_segundos_exactos = total_segundos
            registro.duracion_minutos = max(1, round(total_segundos / 60))
        else:
            # Sesión registrada a mano: la duración se edita directo.
            duracion_minutos = request.form.get("duracion_minutos")
            if not duracion_minutos:
                flash("Indica la duración.")
                return redirect(url_for("estadisticas.editar_registro", registro_id=registro.id))
            registro.duracion_minutos = int(duracion_minutos)

        db.session.commit()

        flash("Registro actualizado.")
        return redirect(url_for("estadisticas.historial"))

    detalle_display = [
        {
            "id": d.id,
            "nombre": d.rutina_actividad.actividad.nombre,
            "min": d.duracion_segundos // 60,
            "seg": d.duracion_segundos % 60,
        }
        for d in registro.detalles
    ]

    return render_template("estadisticas/editar_registro.html", registro=registro, detalle_display=detalle_display)


@estadisticas_bp.route("/eliminar/<int:registro_id>", methods=["POST"])
@login_required
def eliminar_registro(registro_id):
    registro = RegistroActividad.query.filter_by(id=registro_id, usuario_id=current_user.id).first_or_404()

    db.session.delete(registro)
    db.session.commit()

    flash("Registro eliminado.")
    return redirect(url_for("estadisticas.historial"))