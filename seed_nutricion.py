"""
Script para cargar consejos de nutrición de ejemplo.
Se corre una sola vez (o para actualizar el catálogo) con:
    python seed_nutricion.py
"""

from app import create_app
from extensions import db
from models import ConsejoNutricion

consejos_ejemplo = [
    # --- BAJAR DE PESO ---
    {"objetivo": "bajar_peso", "titulo": "Déficit calórico moderado",
     "descripcion": "Consume entre 300 y 500 calorías menos de las que gastas al día. Un déficit muy agresivo puede hacerte perder músculo junto con la grasa."},
    {"objetivo": "bajar_peso", "titulo": "Prioriza la proteína",
     "descripcion": "Mantener un buen consumo de proteína te ayuda a conservar masa muscular mientras bajas de peso, y da más saciedad que otros macronutrientes."},
    {"objetivo": "bajar_peso", "titulo": "Aumenta la fibra",
     "descripcion": "Verduras, legumbres y granos enteros te ayudan a sentirte satisfecho con menos calorías totales."},
    {"objetivo": "bajar_peso", "titulo": "Cuidado con las calorías líquidas",
     "descripcion": "Refrescos, jugos y bebidas azucaradas suman calorías rápido sin darte saciedad. El agua debe ser tu bebida principal."},
    {"objetivo": "bajar_peso", "titulo": "No te saltes comidas",
     "descripcion": "Saltarte comidas puede llevarte a comer de más después. Mejor distribuye tus calorías en comidas regulares durante el día."},

    # --- GANAR MASA MUSCULAR ---
    {"objetivo": "ganar_masa", "titulo": "Superávit calórico controlado",
     "descripcion": "Consume entre 250 y 500 calorías extra al día. Un superávit muy grande solo te hará ganar más grasa sin más músculo."},
    {"objetivo": "ganar_masa", "titulo": "1.6-2.2 g de proteína por kg de peso",
     "descripcion": "Es el rango que la evidencia respalda para maximizar la síntesis de proteína muscular en personas que entrenan fuerza."},
    {"objetivo": "ganar_masa", "titulo": "No le tengas miedo a los carbohidratos",
     "descripcion": "Los carbohidratos son tu principal fuente de energía para entrenar con intensidad y recuperarte entre sesiones."},
    {"objetivo": "ganar_masa", "titulo": "Distribuye la proteína en el día",
     "descripcion": "Repartir la proteína en 3-4 comidas es más efectivo para la síntesis muscular que concentrarla en una sola comida grande."},
    {"objetivo": "ganar_masa", "titulo": "La consistencia importa más que la perfección",
     "descripcion": "Ganar masa muscular es un proceso lento. Es mejor mantener un superávit moderado por meses que buscar resultados rápidos."},

    # --- MANTENIMIENTO ---
    {"objetivo": "mantenimiento", "titulo": "Come acorde a tu gasto energético",
     "descripcion": "El objetivo es que las calorías que consumes sean similares a las que gastas, para mantener tu peso estable."},
    {"objetivo": "mantenimiento", "titulo": "Prioriza alimentos poco procesados",
     "descripcion": "Una dieta basada en alimentos frescos y mínimamente procesados facilita mantener un peso estable a largo plazo."},
    {"objetivo": "mantenimiento", "titulo": "Mantén un consumo de proteína adecuado",
     "descripcion": "Aunque no busques ganar músculo, la proteína ayuda a conservar la masa muscular que ya tienes con la edad."},
    {"objetivo": "mantenimiento", "titulo": "Hidratación constante",
     "descripcion": "Tomar suficiente agua durante el día apoya el metabolismo y ayuda a distinguir el hambre real de la sed."},
    {"objetivo": "mantenimiento", "titulo": "Flexibilidad sin descontrol",
     "descripcion": "Mantener un peso estable no significa comer siempre igual — puedes tener flexibilidad ocasional sin que afecte tu progreso general."},

    # --- RESISTENCIA / CARDIO ---
    {"objetivo": "resistencia", "titulo": "Carga de carbohidratos antes de sesiones largas",
     "descripcion": "Antes de entrenamientos de resistencia prolongados, un consumo mayor de carbohidratos te da más reservas de energía disponibles."},
    {"objetivo": "resistencia", "titulo": "Hidratación con electrolitos",
     "descripcion": "En sesiones largas o con mucho sudor, el agua sola no siempre basta — considera reponer sodio y otros electrolitos."},
    {"objetivo": "resistencia", "titulo": "Come algo ligero antes de entrenar",
     "descripcion": "Un snack con carbohidratos de fácil digestión 1-2 horas antes puede mejorar tu rendimiento en sesiones de cardio."},
    {"objetivo": "resistencia", "titulo": "Recuperación con carbohidratos y proteína",
     "descripcion": "Después de entrenar resistencia, combinar ambos macronutrientes ayuda a reponer energía y reparar tejido muscular."},
    {"objetivo": "resistencia", "titulo": "No descuides el hierro",
     "descripcion": "Los deportistas de resistencia tienen mayor riesgo de niveles bajos de hierro. Incluye fuentes como carnes magras, legumbres y verduras de hoja verde."},
]

app = create_app()

with app.app_context():
    for datos in consejos_ejemplo:
        existente = ConsejoNutricion.query.filter_by(titulo=datos["titulo"]).first()
        if not existente:
            db.session.add(ConsejoNutricion(**datos))

    db.session.commit()
    print(f"Listo: {len(consejos_ejemplo)} consejos verificados/cargados.")