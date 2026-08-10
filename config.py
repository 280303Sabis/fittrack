import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Clave usada para firmar sesiones/cookies. En producción, cámbiala
    # y ponla como variable de entorno, no aquí en texto plano.
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-de-desarrollo-cambiar-en-produccion")

    # Base de datos MySQL local
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/fittrack_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False