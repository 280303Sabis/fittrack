import time

from models import Usuario, Actividad, Rutina, RutinaActividad, RegistroActividad


class TestRendimiento:
    """Pruebas de rendimiento: miden el tiempo de respuesta de
    operaciones específicas bajo condiciones normales de uso."""

    def test_catalogo_responde_rapido(self, client, db):
        """El catálogo de actividades (104 registros) debe cargar en
        menos de 1 segundo, incluso sin optimizaciones adicionales."""
        for i in range(104):
            db.session.add(Actividad(
                nombre=f"Ejercicio {i}", categoria="pesas", grupo_muscular="Pecho",
                descripcion="Descripción de prueba",
            ))
        db.session.commit()

        inicio = time.time()
        respuesta = client.get("/actividades/?categoria=pesas&grupo_muscular=Pecho")
        duracion = time.time() - inicio

        assert respuesta.status_code == 200
        assert duracion < 1.0, f"El catálogo tardó {duracion:.3f}s, se esperaba menos de 1s"

    def test_estadisticas_con_historial_grande(self, client, db):
        """Las estadísticas recorren TODOS los registros del usuario en
        Python (no en SQL agregado). Esta prueba mide cuánto tarda con
        un historial de 200 sesiones, para detectar si en el futuro se
        vuelve necesario optimizar esa consulta."""
        usuario = Usuario(nombre="Usuario Carga", email="carga@test.com", objetivo="bajar_peso")
        usuario.set_password("Fitness2026!")
        usuario.confirmado = True
        db.session.add(usuario)
        db.session.commit()

        rutina = Rutina(usuario_id=usuario.id, nombre="Rutina de carga")
        db.session.add(rutina)
        db.session.commit()

        for i in range(200):
            db.session.add(RegistroActividad(
                usuario_id=usuario.id, rutina_id=rutina.id, duracion_minutos=30,
            ))
        db.session.commit()

        client.post("/auth/login", data={"email": "carga@test.com", "password": "Fitness2026!"})

        inicio = time.time()
        respuesta = client.get("/estadisticas/")
        duracion = time.time() - inicio

        assert respuesta.status_code == 200
        assert duracion < 2.0, f"Estadísticas con 200 registros tardó {duracion:.3f}s, se esperaba menos de 2s"