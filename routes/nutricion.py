from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import ConsejoNutricion

nutricion_bp = Blueprint("nutricion", __name__, url_prefix="/nutricion")

NOMBRES_OBJETIVO = {
    "bajar_peso": "Bajar de peso",
    "ganar_masa": "Aumentar masa muscular",
    "mantenimiento": "Mantenimiento",
    "resistencia": "Resistencia / cardio",
}


@nutricion_bp.route("/")
@login_required
def consejos():
    consejos = ConsejoNutricion.query.filter_by(objetivo=current_user.objetivo).all()
    objetivo_actual = NOMBRES_OBJETIVO.get(current_user.objetivo, current_user.objetivo)

    return render_template(
        "nutricion/consejos.html",
        consejos=consejos,
        objetivo_actual=objetivo_actual,
    )