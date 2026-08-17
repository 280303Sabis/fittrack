from models import Usuario


class TestEsfuerzo:
    """Pruebas de esfuerzo: evalúan el comportamiento del sistema ante
    un volumen alto de peticiones repetidas en poco tiempo."""

    def test_multiples_registros_seguidos(self, client, db):
        """Simula 50 registros de usuario seguidos, uno tras otro, y
        confirma que el sistema los procese todos correctamente sin
        degradarse ni mezclar datos entre peticiones."""
        for i in range(50):
            respuesta = client.post("/auth/registro", data={
                "nombre": f"Usuario Esfuerzo {i}",
                "email": f"esfuerzo{i}@test.com",
                "password": "Fitness2026!",
                "objetivo": "bajar_peso",
                "acepta_privacidad": "on",
            })
            assert respuesta.status_code in (200, 302)

        total = Usuario.query.filter(Usuario.email.like("esfuerzo%@test.com")).count()
        assert total == 50, f"Se esperaban 50 usuarios creados, se encontraron {total}"

    def test_intentos_login_repetidos_no_rompen_el_sistema(self, client, db):
        """Simula 20 intentos de login fallidos seguidos contra la misma
        cuenta (más allá del límite de bloqueo de 3), confirmando que el
        sistema siga respondiendo de forma estable y sin errores, aunque
        la cuenta se mantenga bloqueada durante todos los intentos extra."""
        usuario = Usuario(nombre="Usuario Esfuerzo Login", email="esfuerzologin@test.com", objetivo="bajar_peso")
        usuario.set_password("Fitness2026!")
        usuario.confirmado = True
        db.session.add(usuario)
        db.session.commit()

        for _ in range(20):
            respuesta = client.post("/auth/login", data={
                "email": "esfuerzologin@test.com", "password": "Incorrecta1!",
            })
            assert respuesta.status_code == 302  # siempre redirige, nunca truena