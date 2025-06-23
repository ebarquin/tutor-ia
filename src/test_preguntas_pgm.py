from src.apuntes.scripts.rag_local import obtener_contexto, responder_con_groq

PREGUNTAS = [
    "¿Qué tipos de políticas económicas puede aplicar el Estado?",
    "¿Cuál es la diferencia entre políticas económicas horizontales y verticales?",
    "¿Qué funciones cumple la política fiscal según el documento?",
    "¿Qué son las políticas de ajuste macroeconómico y cuál es su objetivo?",
    "¿Por qué se considera importante la coordinación entre políticas económicas?",
    "¿Qué implica la sostenibilidad en las empresas de servicios públicos según el texto?",
    "¿Qué papel tiene el sector público en la modernización económica y social?",
    "¿Cómo se relaciona la política de infraestructuras con el crecimiento económico?",
    "¿Qué efectos puede tener la emisión de deuda pública en la economía?",
    "¿Qué se entiende por intervención estatal en el mercado y qué formas puede adoptar?",
]

MATERIA = "Economía"
TEMA = "Economía Política"

for i, pregunta in enumerate(PREGUNTAS, 1):
    print(f"\n🔹 Pregunta {i}: {pregunta}\n")
    contexto, advertencia = obtener_contexto(MATERIA, TEMA, pregunta)

    if advertencia:
        print("⚠️", advertencia)
        continue

    print("⏳ Generando respuesta...\n")
    respuesta = responder_con_groq(MATERIA, pregunta, contexto)
    print("🤖 Respuesta generada:\n")
    print(respuesta)