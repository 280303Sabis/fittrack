from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db

perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")


def kg_a_lb(kg):
    return round(kg * 2.20462, 1) if kg else None


def lb_a_kg(lb):
    return round(lb / 2.20462, 1) if lb else None


def cm_a_in(cm):
    return round(cm / 2.54, 1) if cm else None


def in_a_cm(inches):
    return round(inches * 2.54, 1) if inches else None


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
        peso = request.form.get("peso_kg")
        altura = request.form.get("altura_cm")
        edad = request.form.get("edad")
        objetivo = request.form.get("objetivo")

        if not nombre or not objetivo:
            flash("Nombre y objetivo son obligatorios.")
            return redirect(url_for("perfil.ver"))

        current_user.nombre = nombre
        current_user.edad = int(edad) if edad else None
        current_user.objetivo = objetivo

        # El usuario captura en su unidad preferida; siempre guardamos en kg/cm
        if current_user.unidad_medida == "imperial":
            current_user.peso_kg = lb_a_kg(float(peso)) if peso else None
            current_user.altura_cm = in_a_cm(float(altura)) if altura else None
        else:
            current_user.peso_kg = float(peso) if peso else None
            current_user.altura_cm = float(altura) if altura else None

        db.session.commit()

        flash("Tu perfil fue actualizado.")
        return redirect(url_for("perfil.ver"))

    # Mostramos los valores convertidos a la unidad preferida del usuario
    if current_user.unidad_medida == "imperial":
        peso_mostrar = kg_a_lb(current_user.peso_kg)
        altura_mostrar = cm_a_in(current_user.altura_cm)
    else:
        peso_mostrar = current_user.peso_kg
        altura_mostrar = current_user.altura_cm

    return render_template(
        "perfil/ver.html",
        nombres_objetivo=NOMBRES_OBJETIVO,
        peso_mostrar=peso_mostrar,
        altura_mostrar=altura_mostrar,
    )