from extensions import db


class ConsejoNutricion(db.Model):
    __tablename__ = "consejos_nutricion"

    id = db.Column(db.Integer, primary_key=True)
    objetivo = db.Column(db.String(30), nullable=False)  # bajar_peso, ganar_masa, mantenimiento, resistencia
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<ConsejoNutricion {self.titulo} ({self.objetivo})>"