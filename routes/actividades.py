import unicodedata

from flask import Blueprint, render_template, request
from sqlalchemy import func

from extensions import db
from models import Actividad

actividades_bp = Blueprint("actividades", __name__, url_prefix="/actividades")

NOMBRES_CATEGORIA = {
    "pesas": "Pesas / Gimnasio",
    "crossfit": "Crossfit",
    "cardio": "Cardio",
}
ORDEN_CATEGORIA = {"pesas": 0, "crossfit": 1, "cardio": 2}


def slug_grupo(nombre):
    """Convierte 'Cuádriceps' en 'cuadriceps' para encontrar su archivo de ícono."""
    normalizado = unicodedata.normalize("NFKD", nombre)
    sin_acentos = "".join(c for c in normalizado if not unicodedata.combining(c))
    return sin_acentos.lower().replace(" ", "_")


@actividades_bp.route("/")
def lista():
    categoria = request.args.get("categoria")
    grupo_muscular = request.args.get("grupo_muscular")
    # Si viene un rutina_id, significa que estamos eligiendo ejercicios
    # PARA esa rutina específica (en vez de solo explorar el catálogo).
    rutina_id = request.args.get("rutina_id", type=int)

    categorias_selector = None
    grupos_selector = None
    actividades = []

    if not categoria:
        conteo = db.session.query(Actividad.categoria, func.count(Actividad.id)).group_by(Actividad.categoria).all()
        categorias_selector = sorted(
            [{"nombre": c, "etiqueta": NOMBRES_CATEGORIA.get(c, c), "cantidad": n} for c, n in conteo],
            key=lambda x: ORDEN_CATEGORIA.get(x["nombre"], 99),
        )

    elif categoria == "pesas" and not grupo_muscular:
        conteo = (
            db.session.query(Actividad.grupo_muscular, func.count(Actividad.id))
            .filter(Actividad.categoria == "pesas")
            .group_by(Actividad.grupo_muscular)
            .order_by(Actividad.grupo_muscular)
            .all()
        )
        grupos_selector = [
            {"nombre": g, "cantidad": c, "icono": slug_grupo(g)} for g, c in conteo
        ]

    else:
        query = Actividad.query.filter_by(categoria=categoria)
        if grupo_muscular:
            query = query.filter_by(grupo_muscular=grupo_muscular)
        actividades = query.order_by(Actividad.nombre).all()

    return render_template(
        "actividades/lista.html",
        actividades=actividades,
        categorias_selector=categorias_selector,
        grupos_selector=grupos_selector,
        categoria_actual=categoria,
        grupo_actual=grupo_muscular,
        rutina_id=rutina_id,
    )