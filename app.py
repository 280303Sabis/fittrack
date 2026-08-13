from flask import Flask, render_template

from config import Config
from extensions import db, login_manager
from models import Usuario


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
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.actividades import actividades_bp
    app.register_blueprint(actividades_bp)

    from routes.rutinas import rutinas_bp
    app.register_blueprint(rutinas_bp)

    # Flask-Login usa esto para saber quién es el usuario logueado en
    # cada request, a partir del id que guarda en la sesión.
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    @app.route("/")
    def home():
        return render_template("home.html")

    # Crear las tablas si no existen (en MySQL, base de datos fittrack_db)
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)