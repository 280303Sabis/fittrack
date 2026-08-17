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
            "acepta_privacidad": "on",
        }, follow_redirects=True)

        assert respuesta.status_code == 200
        usuario = Usuario.query.filter_by(email="prueba@test.com").first()
        assert usuario is not None
        assert usuario.nombre == "Usuario Prueba"
        # La contraseña nunca debe guardarse en texto plano
        assert usuario.password_hash != "Fitness2026!"
        # Recién registrado, la cuenta debe quedar sin confirmar
        assert usuario.confirmado is False

    def test_registro_sin_aceptar_privacidad_rechazado(self, client, db):
        respuesta = client.post("/auth/registro", data={
            "nombre": "Usuario Sin Aceptar", "email": "sinaceptar@test.com",
            "password": "Fitness2026!", "objetivo": "bajar_peso",
            # sin acepta_privacidad
        }, follow_redirects=True)

        assert b"Aviso de Privacidad" in respuesta.data
        usuario = Usuario.query.filter_by(email="sinaceptar@test.com").first()
        assert usuario is None

    def test_registro_correo_duplicado(self, client, db):
        client.post("/auth/registro", data={
            "nombre": "Primero", "email": "duplicado@test.com",
            "password": "Fitness2026!", "objetivo": "bajar_peso",
            "acepta_privacidad": "on",
        })
        respuesta = client.post("/auth/registro", data={
            "nombre": "Segundo", "email": "duplicado@test.com",
            "password": "Otra2026!", "objetivo": "mantenimiento",
            "acepta_privacidad": "on",
        }, follow_redirects=True)

        assert b"Ya existe una cuenta con ese correo" in respuesta.data
        # Solo debe existir un usuario con ese correo, no dos
        assert Usuario.query.filter_by(email="duplicado@test.com").count() == 1

    def test_registro_password_debil_rechazada(self, client, db):
        client.post("/auth/registro", data={
            "nombre": "Usuario Debil", "email": "debil@test.com",
            "password": "abc123", "objetivo": "bajar_peso",
            "acepta_privacidad": "on",
        })
        usuario = Usuario.query.filter_by(email="debil@test.com").first()
        assert usuario is None


class TestLogin:
    def _registrar_y_confirmar(self, client, db, email, password="Fitness2026!"):
        """Auxiliar: registra un usuario y confirma su cuenta directamente
        en la base de datos, simulando que ya dio clic en el link del
        correo de confirmación (sin depender de enviar un correo real)."""
        client.post("/auth/registro", data={
            "nombre": "Usuario Login", "email": email,
            "password": password, "objetivo": "bajar_peso",
            "acepta_privacidad": "on",
        })
        usuario = Usuario.query.filter_by(email=email).first()
        usuario.confirmado = True
        db.session.commit()
        return usuario

    def test_login_requiere_cuenta_confirmada(self, client, db):
        client.post("/auth/registro", data={
            "nombre": "Sin Confirmar", "email": "sinconfirmar@test.com",
            "password": "Fitness2026!", "objetivo": "bajar_peso",
            "acepta_privacidad": "on",
        })
        respuesta = client.post("/auth/login", data={
            "email": "sinconfirmar@test.com", "password": "Fitness2026!",
        }, follow_redirects=True)

        assert b"Debes confirmar tu cuenta" in respuesta.data

    def test_login_exitoso(self, client, db):
        self._registrar_y_confirmar(client, db, "login@test.com")

        respuesta = client.post("/auth/login", data={
            "email": "login@test.com", "password": "Fitness2026!",
        }, follow_redirects=True)

        assert b"Hola de nuevo" in respuesta.data

    def test_login_password_incorrecta(self, client, db):
        self._registrar_y_confirmar(client, db, "login2@test.com")

        respuesta = client.post("/auth/login", data={
            "email": "login2@test.com", "password": "ContraseñaMala1!",
        }, follow_redirects=True)

        assert b"Correo o contrase\xc3\xb1a incorrectos" in respuesta.data

    def test_login_se_bloquea_tras_3_intentos_fallidos(self, client, db):
        self._registrar_y_confirmar(client, db, "bloqueo@test.com")

        for _ in range(3):
            client.post("/auth/login", data={
                "email": "bloqueo@test.com", "password": "Incorrecta1!",
            })

        # El 4º intento, aunque la contraseña sea correcta, debe rechazarse
        respuesta = client.post("/auth/login", data={
            "email": "bloqueo@test.com", "password": "Fitness2026!",
        }, follow_redirects=True)

        assert b"bloqueada" in respuesta.data


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
            "acepta_privacidad": "on",
        })
        usuario = Usuario.query.filter_by(email="rutina@test.com").first()
        usuario.confirmado = True
        db.session.commit()

        client.post("/auth/login", data={
            "email": "rutina@test.com", "password": "Fitness2026!",
        })

        respuesta = client.post("/rutinas/nueva", data={
            "nombre": "Rutina de prueba",
        }, follow_redirects=True)

        assert respuesta.status_code == 200
        rutina = Rutina.query.filter_by(nombre="Rutina de prueba").first()
        assert rutina is not None
        assert rutina.usuario.email == "rutina@test.com"