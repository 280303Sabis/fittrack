from models import Usuario, Rutina


class TestRegistro:
    """Pruebas de caja negra: no nos importa CÓMO está implementado el
    registro por dentro, solo probamos las entradas y salidas esperadas
    desde afuera, como lo haría un usuario real."""

    def test_registro_exitoso(self, client, db):
        respuesta = client.post("/auth/registro", data={
            "nombre": "Usuario Prueba",
            "email": "prueba@test.com",
            "password": "Fitness2026!",
            "objetivo": "bajar_peso",
        }, follow_redirects=True)

        assert respuesta.status_code == 200
        usuario = Usuario.query.filter_by(email="prueba@test.com").first()
        assert usuario is not None
        assert usuario.nombre == "Usuario Prueba"
        # La contraseña nunca debe guardarse en texto plano
        assert usuario.password_hash != "Fitness2026!"

    def test_registro_correo_duplicado(self, client, db):
        client.post("/auth/registro", data={
            "nombre": "Primero", "email": "duplicado@test.com",
            "password": "Fitness2026!", "objetivo": "bajar_peso",
        })
        respuesta = client.post("/auth/registro", data={
            "nombre": "Segundo", "email": "duplicado@test.com",
            "password": "Otra2026!", "objetivo": "mantenimiento",
        }, follow_redirects=True)

        assert b"Ya existe una cuenta con ese correo" in respuesta.data
        # Solo debe existir un usuario con ese correo, no dos
        assert Usuario.query.filter_by(email="duplicado@test.com").count() == 1

    def test_registro_password_debil_rechazada(self, client, db):
        client.post("/auth/registro", data={
            "nombre": "Usuario Debil", "email": "debil@test.com",
            "password": "abc123", "objetivo": "bajar_peso",
        })
        usuario = Usuario.query.filter_by(email="debil@test.com").first()
        assert usuario is None


class TestLogin:
    def test_login_exitoso(self, client, db):
        client.post("/auth/registro", data={
            "nombre": "Usuario Login", "email": "login@test.com",
            "password": "Fitness2026!", "objetivo": "bajar_peso",
        })
        client.get("/auth/logout")

        respuesta = client.post("/auth/login", data={
            "email": "login@test.com", "password": "Fitness2026!",
        }, follow_redirects=True)

        assert b"Hola de nuevo" in respuesta.data

    def test_login_password_incorrecta(self, client, db):
        client.post("/auth/registro", data={
            "nombre": "Usuario Login2", "email": "login2@test.com",
            "password": "Fitness2026!", "objetivo": "bajar_peso",
        })
        client.get("/auth/logout")

        respuesta = client.post("/auth/login", data={
            "email": "login2@test.com", "password": "ContraseñaMala1!",
        }, follow_redirects=True)

        assert b"Correo o contrase\xc3\xb1a incorrectos" in respuesta.data


class TestRutinas:
    """Prueba de integración: varias piezas trabajando juntas (auth +
    modelo Rutina + base de datos) en un flujo completo."""

    def test_crear_rutina_requiere_login(self, client, db):
        # Sin haber iniciado sesión, debe redirigir al login (no crear nada)
        respuesta = client.get("/rutinas/", follow_redirects=True)
        assert b"Iniciar sesi" in respuesta.data

    def test_crear_rutina_exitosa(self, client, db):
        client.post("/auth/registro", data={
            "nombre": "Usuario Rutina", "email": "rutina@test.com",
            "password": "Fitness2026!", "objetivo": "ganar_masa",
        })

        respuesta = client.post("/rutinas/nueva", data={
            "nombre": "Rutina de prueba",
        }, follow_redirects=True)

        assert respuesta.status_code == 200
        rutina = Rutina.query.filter_by(nombre="Rutina de prueba").first()
        assert rutina is not None
        assert rutina.usuario.email == "rutina@test.com"