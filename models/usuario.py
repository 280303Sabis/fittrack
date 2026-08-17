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

    # Tipo de meta semanal: 'minutos' o 'dias'
    tipo_meta = db.Column(db.String(10), nullable=True, default="minutos")

    # Meta en días entrenados por semana (se usa solo si tipo_meta == 'dias')
    meta_dias_semana = db.Column(db.Integer, nullable=True, default=5)

    # Preferencia de unidades: 'metrico' (kg/cm) o 'imperial' (lb/in)
    unidad_medida = db.Column(db.String(10), nullable=True, default="metrico")

    # Para recuperación de contraseña: token temporal + cuándo se generó
    token_recuperacion = db.Column(db.String(100), nullable=True)
    token_expira = db.Column(db.DateTime, nullable=True)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Si se borra el usuario, se borran automáticamente todas sus rutinas
    # y registros de actividad (protección de datos: al eliminar la cuenta,
    # no quedan datos huérfanos del usuario en la base de datos).
    rutinas = db.relationship("Rutina", backref="usuario", cascade="all, delete-orphan")
    registros_actividad = db.relationship("RegistroActividad", backref="usuario", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.email}>"