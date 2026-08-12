from extensions import db


class Actividad(db.Model):
    __tablename__ = "actividades"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    # pesas, crossfit o cardio
    categoria = db.Column(db.String(20), nullable=False)

    # Solo aplica a pesas/crossfit (ej. cuádriceps, pecho, espalda)
    grupo_muscular = db.Column(db.String(50), nullable=True)

    descripcion = db.Column(db.Text, nullable=True)

    # Nombre del archivo de imagen dentro de static/img/actividades/
    imagen = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        return f"<Actividad {self.nombre} ({self.categoria})>"