from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db

perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")

NOMBRES_OBJETIVO = {
    "bajar_peso": "Bajar de peso",
    "ganar_masa": "Aumentar masa muscular",
    "mantenimiento": "Mantenimiento",
    "resistencia": "Resistencia / cardio",
}


@perfil_bp.route("/", methods=["GET", "POST"])
@login_required
def ver():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        peso_kg = request.form.get("peso_kg")
        altura_cm = request.form.get("altura_cm")
        edad = request.form.get("edad")
        objetivo = request.form.get("objetivo")

        if not nombre or not objetivo:
            flash("Nombre y objetivo son obligatorios.")
            return redirect(url_for("perfil.ver"))

        current_user.nombre = nombre
        current_user.peso_kg = float(peso_kg) if peso_kg else None
        current_user.altura_cm = float(altura_cm) if altura_cm else None
        current_user.edad = int(edad) if edad else None
        current_user.objetivo = objetivo

        db.session.commit()

        flash("Tu perfil fue actualizado.")
        return redirect(url_for("perfil.ver"))

    return render_template("perfil/ver.html", nombres_objetivo=NOMBRES_OBJETIVO)