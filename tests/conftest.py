import pytest

from app import create_app
from extensions import db as _db


@pytest.fixture
def app():
    """
    Crea una instancia de la app configurada para pruebas: usa SQLite en
    memoria (no toca tu base de datos MySQL real) y desactiva CSRF/envío
    de correos reales para que las pruebas corran solas, sin depender de
    Gmail ni de tu base de datos de desarrollo.
    """
    test_app = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "MAIL_SUPPRESS_SEND": True,
    })

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de pruebas: simula peticiones HTTP sin levantar un servidor real."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Acceso directo a la base de datos de prueba, para preparar datos antes de un test."""
    return _db