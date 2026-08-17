from utils import password_es_segura
from routes.estadisticas import formato_mm_ss


class TestPasswordSegura:
    """Pruebas unitarias de caja blanca: conocemos la lógica interna
    (las 4 condiciones) y probamos cada una por separado."""

    def test_password_valida(self):
        es_segura, mensaje = password_es_segura("Fitness2026!")
        assert es_segura is True
        assert mensaje is None

    def test_password_muy_corta(self):
        es_segura, mensaje = password_es_segura("Ab1!")
        assert es_segura is False
        assert "8 caracteres" in mensaje

    def test_password_sin_mayuscula(self):
        es_segura, mensaje = password_es_segura("fitness2026!")
        assert es_segura is False
        assert "mayúscula" in mensaje

    def test_password_sin_numero(self):
        es_segura, mensaje = password_es_segura("Fitness!!")
        assert es_segura is False
        assert "número" in mensaje

    def test_password_sin_caracter_especial(self):
        es_segura, mensaje = password_es_segura("Fitness2026")
        assert es_segura is False
        assert "especial" in mensaje


class TestFormatoTiempo:
    """Pruebas unitarias de caja blanca: verificamos que la conversión
    de segundos a formato MM:SS sea matemáticamente correcta."""

    def test_menos_de_un_minuto(self):
        assert formato_mm_ss(45) == "00:45"

    def test_exactamente_un_minuto(self):
        assert formato_mm_ss(60) == "01:00"

    def test_minutos_y_segundos(self):
        assert formato_mm_ss(125) == "02:05"

    def test_cero_segundos(self):
        assert formato_mm_ss(0) == "00:00"

    def test_una_hora(self):
        assert formato_mm_ss(3600) == "60:00"