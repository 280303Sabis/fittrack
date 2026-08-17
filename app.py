from flask import Flask, render_template

from config import Config
from extensions import db, login_manager, mail
from models import Usuario


def create_app(config_extra=None):
    """
    Application factory: arma y devuelve la app Flask ya configurada.
    Usar una función (en vez de crear la app directo en el módulo) facilita
    las pruebas (tests) porque se puede crear una instancia nueva por test.

    config_extra: diccionario opcional para sobrescribir configuración,
    usado por las pruebas para apuntar a una base de datos de prueba en
    vez de la base de datos real.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_extra:
        app.config.update(config_extra)

    # Conectar extensiones a esta instancia de la app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # --- Blueprints ---
    # Cada módulo (auth, perfil, actividades, rutinas, etc.) se registra
    # aquí conforme se vaya construyendo en las siguientes fases.
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.actividades import actividades_bp
    app.register_blueprint(actividades_bp)

    from routes.rutinas import rutinas_bp
    app.register_blueprint(rutinas_bp)

    from routes.estadisticas import estadisticas_bp
    app.register_blueprint(estadisticas_bp)

    from routes.nutricion import nutricion_bp
    app.register_blueprint(nutricion_bp)

    from routes.perfil import perfil_bp
    app.register_blueprint(perfil_bp)

    from routes.configuracion import configuracion_bp
    app.register_blueprint(configuracion_bp)

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