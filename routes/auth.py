import secrets
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from flask_mail import Message

from extensions import db, mail
from models import Usuario
from utils import password_es_segura

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

        es_segura, mensaje_error = password_es_segura(password)
        if not es_segura:
            flash(mensaje_error)
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


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Cerraste sesión correctamente.")
    return redirect(url_for("home"))


@auth_bp.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        email = request.form.get("email")
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            token = secrets.token_urlsafe(32)
            usuario.token_recuperacion = token
            usuario.token_expira = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            link = url_for("auth.restablecer", token=token, _external=True)
            mensaje = Message(
                subject="Recuperar contraseña — FitTrack",
                recipients=[usuario.email],
                body=f"Hola {usuario.nombre},\n\nPara restablecer tu contraseña, entra a este link (válido por 1 hora):\n{link}\n\nSi no pediste esto, ignora este correo.",
            )
            mail.send(mensaje)

        # Mismo mensaje exista o no el correo, por seguridad
        flash("Si ese correo está registrado, te enviamos un link para recuperar tu contraseña.")
        return redirect(url_for("auth.login"))

    return render_template("auth/recuperar.html")


@auth_bp.route("/restablecer/<token>", methods=["GET", "POST"])
def restablecer(token):
    usuario = Usuario.query.filter_by(token_recuperacion=token).first()

    if not usuario or not usuario.token_expira or usuario.token_expira < datetime.utcnow():
        flash("El link de recuperación no es válido o ya expiró.")
        return redirect(url_for("auth.recuperar"))

    if request.method == "POST":
        password = request.form.get("password")
        if not password:
            flash("Escribe una nueva contraseña.")
            return redirect(url_for("auth.restablecer", token=token))

        es_segura, mensaje_error = password_es_segura(password)
        if not es_segura:
            flash(mensaje_error)
            return redirect(url_for("auth.restablecer", token=token))

        usuario.set_password(password)
        usuario.token_recuperacion = None
        usuario.token_expira = None
        db.session.commit()

        flash("Tu contraseña fue actualizada. Ya puedes iniciar sesión.")
        return redirect(url_for("auth.login"))

    return render_template("auth/restablecer.html", token=token)