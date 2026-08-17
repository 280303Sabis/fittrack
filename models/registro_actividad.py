from datetime import datetime

from extensions import db


class RegistroActividad(db.Model):
    """
    Cada vez que un usuario completa una rutina, se guarda una fila aquí.
    Esta tabla es la que alimenta las estadísticas (minutos por semana,
    racha de días) más adelante.
    """
    __tablename__ = "registros_actividad"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    rutina_id = db.Column(db.Integer, db.ForeignKey("rutinas.id"), nullable=False)

    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    duracion_minutos = db.Column(db.Integer, nullable=False)
    duracion_segundos_exactos = db.Column(db.Integer, nullable=True)  # tiempo exacto en segundos, solo cuando viene del cronómetro

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    rutina = db.relationship("Rutina")
    detalles = db.relationship("RegistroActividadDetalle", backref="registro", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RegistroActividad rutina={self.rutina_id} fecha={self.fecha}>"