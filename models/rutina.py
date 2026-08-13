from datetime import datetime

from extensions import db


class Rutina(db.Model):
    __tablename__ = "rutinas"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación: una rutina tiene muchas "líneas" de ejercicio (RutinaActividad).
    # cascade="all, delete-orphan" significa que si borras la rutina, se
    # borran automáticamente todas sus líneas de ejercicio con ella.
    actividades = db.relationship(
        "RutinaActividad", backref="rutina", cascade="all, delete-orphan",
        order_by="RutinaActividad.orden"
    )

    def __repr__(self):
        return f"<Rutina {self.nombre}>"


class RutinaActividad(db.Model):
    """
    Tabla intermedia: representa 'este ejercicio, con estos datos,
    dentro de esta rutina'. Es donde vive series/repeticiones/duración,
    porque esos datos dependen de la combinación rutina+ejercicio, no
    del ejercicio en sí (el mismo ejercicio puede tener distintas
    series en distintas rutinas).
    """
    __tablename__ = "rutina_actividades"

    id = db.Column(db.Integer, primary_key=True)
    rutina_id = db.Column(db.Integer, db.ForeignKey("rutinas.id"), nullable=False)
    actividad_id = db.Column(db.Integer, db.ForeignKey("actividades.id"), nullable=False)

    series = db.Column(db.Integer, nullable=True)
    repeticiones = db.Column(db.Integer, nullable=True)
    duracion_minutos = db.Column(db.Integer, nullable=True)

    orden = db.Column(db.Integer, default=0)

    actividad = db.relationship("Actividad")