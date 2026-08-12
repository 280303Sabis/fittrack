import unicodedata

from flask import Blueprint, render_template, request
from sqlalchemy import func

from extensions import db
from models import Actividad

actividades_bp = Blueprint("actividades", __name__, url_prefix="/actividades")


def slug_grupo(nombre):
    """Convierte 'Cuádriceps' en 'cuadriceps' para encontrar su archivo de ícono."""
    normalizado = unicodedata.normalize("NFKD", nombre)
    sin_acentos = "".join(c for c in normalizado if not unicodedata.combining(c))
    return sin_acentos.lower().replace(" ", "_")


@actividades_bp.route("/")
def lista():
    categoria = request.args.get("categoria")
    grupo_muscular = request.args.get("grupo_muscular")

    query = Actividad.query
    if categoria:
        query = query.filter_by(categoria=categoria)
    if grupo_muscular:
        query = query.filter_by(grupo_muscular=grupo_muscular)

    actividades = query.order_by(Actividad.nombre).all()

    # Si estamos en "pesas" y todavía no se eligió un grupo muscular,
    # no mostramos ejercicios sueltos: mostramos el selector de íconos.
    grupos_selector = None
    if categoria == "pesas" and not grupo_muscular:
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
        actividades = []

    return render_template(
        "actividades/lista.html",
        actividades=actividades,
        grupos_selector=grupos_selector,
        categoria_actual=categoria,
        grupo_actual=grupo_muscular,
    )