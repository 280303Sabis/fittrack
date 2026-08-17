from extensions import db


class RegistroActividadDetalle(db.Model):
    """
    Cuánto tiempo tomó cada ejercicio individual dentro de una sesión
    completada con el cronómetro. Un RegistroActividad (la sesión) puede
    tener varias filas aquí, una por cada ejercicio de la rutina.
    """
    __tablename__ = "registro_actividad_detalle"

    id = db.Column(db.Integer, primary_key=True)
    registro_id = db.Column(db.Integer, db.ForeignKey("registros_actividad.id"), nullable=False)
    rutina_actividad_id = db.Column(db.Integer, db.ForeignKey("rutina_actividades.id"), nullable=False)
    duracion_segundos = db.Column(db.Integer, nullable=False)

    rutina_actividad = db.relationship("RutinaActividad")

    def __repr__(self):
        return f"<RegistroActividadDetalle registro={self.registro_id} linea={self.rutina_actividad_id}>"