from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Datos de perfil (se llenan en la Fase 1, parte de "Perfil")
    peso_kg = db.Column(db.Float, nullable=True)
    altura_cm = db.Column(db.Float, nullable=True)
    edad = db.Column(db.Integer, nullable=True)
    nivel = db.Column(db.String(20), nullable=True)  # principiante, intermedio, avanzado

    # Objetivo: define qué rutinas y consejos de nutrición se le muestran
    objetivo = db.Column(db.String(30), nullable=True)  # bajar_peso, ganar_masa, mantenimiento, resistencia

    # Meta personal de minutos de actividad por semana (para la barra de progreso)
    meta_minutos_semana = db.Column(db.Integer, nullable=True, default=150)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.email}>"