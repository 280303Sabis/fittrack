from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user

from extensions import db
from models import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        peso_kg = request.form.get("peso_kg")
        altura_cm = request.form.get("altura_cm")
        edad = request.form.get("edad")
        objetivo = request.form.get("objetivo")

        # Validación básica: estos 4 son obligatorios
        if not nombre or not email or not password or not objetivo:
            flash("Nombre, correo, contraseña y objetivo son obligatorios.")
            return redirect(url_for("auth.registro"))

        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash("Ya existe una cuenta con ese correo.")
            return redirect(url_for("auth.registro"))

        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            objetivo=objetivo,
            peso_kg=float(peso_kg) if peso_kg else None,
            altura_cm=float(altura_cm) if altura_cm else None,
            edad=int(edad) if edad else None,
        )
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        login_user(nuevo_usuario)
        flash(f"¡Bienvenido, {nombre}! Tu cuenta fue creada.")
        return redirect(url_for("home"))

    return render_template("auth/registro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)
            flash(f"¡Hola de nuevo, {usuario.nombre}!")
            return redirect(url_for("home"))

        flash("Correo o contraseña incorrectos.")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")