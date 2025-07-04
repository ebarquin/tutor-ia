# from src.apuntes.scripts.agents.agent_tools import (
#     generar_desarrollo_subtema_groq,
#     generar_desarrollo_subtema_gpt35,
#     generar_prompt_especifico_groq,
#     evaluar_calidad_desarrollo,
#     generar_clase_magistral_avanzada,
# )

# TITULO = "El Desembarco de Normandía"
# CONTEXTO = (
#     "Durante la Segunda Guerra Mundial, los Aliados planificaron una invasión a gran escala para liberar Europa Occidental de la ocupación nazi."
# )

# print("==== 1. Generando con Groq (prompt general) ====")
# texto_groq = generar_desarrollo_subtema_groq(TITULO, CONTEXTO)
# print(texto_groq)
# calidad_groq = evaluar_calidad_desarrollo(TITULO, texto_groq)
# print(f"Evaluación (Groq): {calidad_groq}\n")

# if calidad_groq == "rico":
#     print("✅ Desarrollo Groq es RICO, no se necesitan más pasos.")
#     final_resultados = [("Groq", texto_groq, calidad_groq)]
# else:
#     print("⚠️ Desarrollo Groq es POBRE. Probando con prompt específico en Groq...")
#     prompt_especifico = generar_prompt_especifico_groq(TITULO, CONTEXTO)
#     texto_groq_especifico = generar_desarrollo_subtema_groq(TITULO, CONTEXTO, prompt_personalizado=prompt_especifico)
#     calidad_groq_especifico = evaluar_calidad_desarrollo(TITULO, texto_groq_especifico)
#     print("==== 2. Generando con Groq (prompt específico) ====")
#     print(texto_groq_especifico)
#     print(f"Evaluación (Groq, prompt específico): {calidad_groq_especifico}\n")

#     if calidad_groq_especifico == "rico":
#         print("✅ Desarrollo Groq (prompt específico) es RICO. Nos quedamos con este resultado.")
#         final_resultados = [
#             ("Groq", texto_groq, calidad_groq),
#             ("Groq+prompt específico", texto_groq_especifico, calidad_groq_especifico)
#         ]
#     else:
#         print("⚠️ Desarrollo Groq (prompt específico) sigue siendo POBRE. Probando con GPT-3.5-turbo (prompt específico)...")
#         texto_gpt_especifico = generar_desarrollo_subtema_gpt35(TITULO, CONTEXTO, prompt_personalizado=prompt_especifico)
#         calidad_gpt_especifico = evaluar_calidad_desarrollo(TITULO, texto_gpt_especifico)
#         print("==== 3. Generando con GPT-3.5-turbo (prompt específico) ====")
#         print(texto_gpt_especifico)
#         print(f"Evaluación (GPT-3.5-turbo, prompt específico): {calidad_gpt_especifico}\n")
#         final_resultados = [
#             ("Groq", texto_groq, calidad_groq),
#             ("Groq+prompt específico", texto_groq_especifico, calidad_groq_especifico),
#             ("GPT-3.5-turbo+prompt específico", texto_gpt_especifico, calidad_gpt_especifico)
#         ]

# print("\n===== RESUMEN ORDENADO POR CALIDAD =====")
# for nombre, texto, calidad in sorted(final_resultados, key=lambda x: x[2], reverse=True):
#     print(f"\n>> [{nombre}] ({calidad.upper()})\n{texto[:400]}{'...' if len(texto) > 400 else ''}")
# print("\n=== Proceso terminado ===")

from src.apuntes.scripts.agents.agent_tools import generar_clase_magistral_avanzada

if __name__ == "__main__":
    # Cambia esto por los nombres reales
    MATERIA = "historia"
    TEMA = "segunda_guerra_mundial"
    MAX_SUBTEMAS = 8   # Puedes cambiarlo según lo que tengas

    print(f"Generando clase magistral avanzada para {MATERIA}/{TEMA} ...\n")
    clase_completa = generar_clase_magistral_avanzada(MATERIA, TEMA, MAX_SUBTEMAS)

    # Imprime solo el comienzo (puedes guardar el texto si es muy largo)
    print(clase_completa[:2000])  # Solo los primeros 2000 caracteres

    # Si quieres, guarda el resultado en un archivo
    with open(f"clase_magistral_{MATERIA}_{TEMA}.md", "w") as f:
        f.write(clase_completa)
    print("\n✅ Clase magistral guardada en archivo Markdown.")