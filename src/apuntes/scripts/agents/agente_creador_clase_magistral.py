from src.apuntes.scripts.agents.agent_tools import generar_desarrollo_orquestado, postprocesar_clase_magistral_groq, limpiar_titulos
from src.apuntes.scripts.crear_vectorstore import cargar_chunks
import time
import sys
import json
from datetime import datetime
import os
from src.config import GROQ_API_KEY


def insertar_clase_magistral_en_json(materia, tema, texto_clase, texto_clase_limpio):
    tema_slug = tema.lower().replace(" ", "_")
    materia_slug = materia.lower().replace(" ", "_")
    ruta_json = f"src/apuntes/rag/chunks/{materia_slug}__{tema_slug}.json"

    # Cargar JSON existente
    with open(ruta_json, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Crear nuevo chunk con ambos textos
    clase_chunk = {
        "page_content": texto_clase,                # original con títulos
        "page_content_audio": texto_clase_limpio,   # versión postprocesada (fluida)
        "metadata": {
            "tipo": "clase_magistral_completa",
            "materia": materia,
            "tema": tema,
            "fecha": datetime.now().isoformat()
        }
    }

    # Añadirlo al final
    chunks.append(clase_chunk)

    # Sobrescribir el archivo
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"✅ Clase magistral (y versión audio) insertada en {ruta_json}")

    # Añadirlo al final
    chunks.append(clase_chunk)


def agente_clase_magistral(materia, tema, max_subtemas=5):
    """
    Orquesta la generación y evaluación de la clase magistral para una materia y tema dados.
    """
    # 1. Cargar chunks y extraer títulos
    chunks = cargar_chunks(materia, tema)
    chunks_filtrados = [c for c in chunks if c.metadata.get("titulo")][:max_subtemas]
    print(f"Títulos encontrados para desarrollar: {[c.metadata.get('titulo') for c in chunks_filtrados]}")

    for i, chunk in enumerate(chunks_filtrados, 1):
        titulo = chunk.metadata.get("titulo")
        contexto_base = chunk.page_content
        print(f"\n--- [{i}/{len(chunks_filtrados)}] Desarrollando: {titulo} ---")
        desarrollo = generar_desarrollo_orquestado(titulo, contexto_base)
        yield {
            "titulo": titulo,
            "desarrollo": desarrollo
        }

if __name__ == "__main__":
    MATERIA = "historia"
    TEMA = "segunda_guerra_mundial"
    MAX_SUBTEMAS = 5

    print(f"Generando clase magistral avanzada para {MATERIA}/{TEMA}...\n")

    subtemas = []
    for subtema in agente_clase_magistral(MATERIA, TEMA, MAX_SUBTEMAS):
        titulo = subtema["titulo"]
        print(f"\n📘 Subtema generado: {titulo}\n")
        print("📝 Desarrollo (primeros 300 caracteres):\n")

        # Imprimir carácter a carácter como si escribiera en vivo
        for c in subtema["desarrollo"][:300]:
            print(c, end="")
            sys.stdout.flush()
            time.sleep(0.01)  # Simula escritura rápida

        print("\n\n--- Esperando siguiente subtema... ---\n")
        time.sleep(0.5)
        subtemas.append(subtema)

    # Construir el texto completo
    texto_clase = "\n\n".join([s["desarrollo"] for s in subtemas])

    # --- POSTPROCESADO CON GROQ ---
    groq_api_key = GROQ_API_KEY
    texto_clase_sin_titulos = limpiar_titulos(texto_clase)
    texto_clase_limpio = postprocesar_clase_magistral_groq(texto_clase_sin_titulos, groq_api_key)


    # Guardar ambos textos en JSON
    insertar_clase_magistral_en_json(MATERIA, TEMA, texto_clase, texto_clase_limpio)