from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Se instancian aquí (sin app todavía) y se conectan a la app en app.py
# con init_app(). Así cualquier archivo (models, routes) puede importar
# "db" o "login_manager" sin crear imports circulares.
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sesión para continuar."