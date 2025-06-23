from src.apuntes.scripts.rag_local import obtener_contexto, responder_con_groq

PREGUNTAS = [
    # ✅ 5 preguntas basadas en el contenido del documento
    "¿Qué fue la operación Barbarroja y qué consecuencias tuvo en el conflicto?",
    "¿Qué papel desempeñaron los Estados Unidos tras el ataque a Pearl Harbor?",
    "¿Cuál fue el resultado de la batalla de Stalingrado y por qué fue relevante?",
    "¿Qué acuerdos se tomaron en las conferencias de Yalta y Potsdam?",
    "¿Qué características tuvo la política de expansión territorial del Eje?",

    # ❌ 5 preguntas que no están en el documento o no tienen relación con el tema
    "¿Cuál fue la influencia del Renacimiento italiano en la Segunda Guerra Mundial?",
    "¿Qué teorías económicas defendía Adam Smith durante la guerra?",
    "¿En qué año cayó el Imperio Romano de Occidente?",
    "¿Qué especies vegetales fueron descubiertas en la Antártida durante la guerra?",
    "¿Cuáles fueron los principales avances tecnológicos del Neolítico?"
]

MATERIA = "Historia"
TEMA = "Segunda Guerra Mundial"

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