from flask import Flask, render_template

from config import Config
from extensions import db, login_manager


def create_app():
    """
    Application factory: arma y devuelve la app Flask ya configurada.
    Usar una función (en vez de crear la app directo en el módulo) facilita
    las pruebas (tests) porque se puede crear una instancia nueva por test.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Conectar extensiones a esta instancia de la app
    db.init_app(app)
    login_manager.init_app(app)

    # --- Blueprints ---
    # Cada módulo (auth, perfil, actividades, rutinas, etc.) se registra
    # aquí conforme se vaya construyendo en las siguientes fases.
    # from routes.auth import auth_bp
    # app.register_blueprint(auth_bp)

    # Flask-Login exige un user_loader en cuanto se inicializa. Este es
    # temporal: en la Fase 1, cuando exista el modelo Usuario, se reemplaza
    # por la carga real del usuario desde la base de datos.
    @login_manager.user_loader
    def load_user(user_id):
        return None

    @app.route("/")
    def home():
        return render_template("home.html")

    # Crear las tablas si no existen (para SQLite en desarrollo)
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)