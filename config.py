import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Clave usada para firmar sesiones/cookies. En producción, cámbiala
    # y ponla como variable de entorno, no aquí en texto plano.
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-de-desarrollo-cambiar-en-produccion")

    # Base de datos SQLite local (archivo database.db en la raíz del proyecto)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False