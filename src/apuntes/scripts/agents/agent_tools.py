from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from pathlib import Path
import os
import json
import re
import uuid
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# Constantes globales
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BASE_DIR = Path(__file__).resolve().parents[4]
VECTORSTORE_DIR = BASE_DIR / "src" / "apuntes" / "rag" / "vectorstores"
api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key)

# --- HELPERS ---

def cargar_vectorstore(materia: str, tema: str):
    ruta = VECTORSTORE_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}"
    if not ruta.exists():
        return None
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    store = FAISS.load_local(str(ruta), embeddings, allow_dangerous_deserialization=True)
    return store

def obtener_todo_contexto_vectorstore(materia: str, tema: str, max_chunks: int = 10) -> str:
    store = cargar_vectorstore(materia, tema)
    if not store:
        return ""
    docs = store.similarity_search("", k=max_chunks)
    contexto = "\n\n".join(doc.page_content.strip() for doc in docs)
    return contexto

def obtener_titulos_vectorstore(materia: str, tema: str, max_chunks: int = 12):
    """Devuelve una lista de títulos únicos de los chunks de un vectorstore."""
    store = cargar_vectorstore(materia, tema)
    if not store:
        return []
    docs = store.similarity_search("", k=max_chunks)
    titulos_unicos = []
    for doc in docs:
        titulo = doc.metadata.get("punto") or doc.metadata.get("titulo") or ""
        if titulo and titulo not in titulos_unicos:
            titulos_unicos.append(titulo)
    return titulos_unicos

def construir_texto_clase_base(titulos: list):
    """Construye el texto base de la clase a partir de los títulos de los chunks."""
    return "\n".join(f"- {t}" for t in titulos if t)

def crear_prompt_profesor(materia: str, tema: str, texto_clase_base: str):
    """Genera el prompt con instrucciones para el LLM."""
    return (
        f"Imagina que eres un profesor universitario, experto en el tema '{tema}' de la asignatura '{materia}', "
        "con un punto paternalista, simpático y algo condescendiente (pero no ofensivo). "
        "Tu misión es explicar el contenido siguiente como si fuera una clase magistral presencial, "
        "comenzando con un saludo cercano, una breve introducción de lo que se va a tratar, "
        "inserta algún comentario divertido o simpático para captar la atención, y termina con un cierre motivador o con humor académico. "
        "Usa frases claras, conecta ideas, haz alguna pregunta retórica, y muestra tu experiencia docente. "
        "El objetivo es que hasta el alumno más despistado comprenda todo, aunque repitas alguna idea importante. "
        "ATENCIÓN: Es MUY importante que el texto tenga al menos 900 palabras reales. Si tienes que alargar, añade ejemplos, anécdotas o explicaciones complementarias relevantes, pero nunca rellenes con paja o repeticiones forzadas.\n\n"
        "Al final de la exposición, añade entre paréntesis el número total de palabras escritas.\n\n"
        f"CONTENIDO BASE DE LA CLASE:\n{texto_clase_base}\n"
        "\n---\nGenera la exposición como si la leyeras en voz alta en clase. No digas que eres una IA. "
        "No expliques qué vas a hacer, simplemente haz la exposición con el tono descrito."
    )

def generar_texto_profesor(prompt, modelo_llm, min_palabras=900, intentos=3):
    """Genera la exposición, reintentando si no se alcanza el mínimo de palabras."""
    texto_profesor = ""
    for i in range(intentos):
        exposicion_llm = modelo_llm.invoke(prompt)
        texto_profesor = exposicion_llm.content if hasattr(exposicion_llm, "content") else str(exposicion_llm)
        num_palabras = len(texto_profesor.split())
        if num_palabras >= min_palabras:
            return texto_profesor
        print(f"⚠️ El texto generado tiene solo {num_palabras} palabras. Reintentando (intento {i+2})...")
        prompt += (
            "\n\n¡IMPORTANTE! El texto anterior NO alcanzó el mínimo requerido. Amplía la exposición hasta superar las 900 palabras reales, "
            "añade explicaciones, ejemplos, historias o analogías, pero no repitas el texto anterior."
        )
    return texto_profesor  # Devuelve lo que haya aunque no llegue al mínimo

def tts_func(
    texto,
    carpeta_destino="audios",
    voz_id="6xftrpatV0jGmFHxDjUv",
    modelo="eleven_multilingual_v2"
):
    """
    Genera un archivo de audio MP3 a partir de un texto, usando ElevenLabs TTS v2.x.
    """
    import uuid
    import os

    api_key = os.getenv("ELEVENLABS_API_KEY")
    client = ElevenLabs(api_key=api_key)

    if voz_id is None:
        raise ValueError("Debes proporcionar el parámetro 'voz_id' (voice_id de ElevenLabs)")

    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
    nombre_archivo = f"clase_magistral_{uuid.uuid4().hex[:8]}.mp3"
    ruta = os.path.join(carpeta_destino, nombre_archivo)
    try:
        audio_stream = client.text_to_speech.stream(
            text=texto,
            voice_id=voz_id,
            model_id=modelo
        )
        with open(ruta, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
        return ruta
    except Exception as e:
        print(f"❌ Error al generar audio: {e}")
        return None
    

# --- TOOLS ---

def analizar_lagunas_en_contexto_tool(materia: str, tema: str, modelo_llm) -> dict:
    contexto = obtener_todo_contexto_vectorstore(materia, tema)
    if not contexto:
        return {"error": "No se encontró información suficiente en los apuntes."}

    prompt = (
        "DEVUELVE SOLO Y ESTRICTAMENTE UN OBJETO JSON como el siguiente ejemplo (NO EXPLICACIONES, NO TÍTULOS):\n"
        "{\n"
        '  "ausencias": ["..."],\n'
        '  "incoherencias": ["..."],\n'
        '  "subtemas_recomendados": ["..."]\n'
        "}\n\n"
        "NO ESCRIBAS NINGUNA PALABRA O COMENTARIO ANTES NI DESPUÉS DEL JSON.\n"
        f"Eres un experto en el tema '{tema}'. "
        "Analiza el siguiente texto extraído de los apuntes de un estudiante y responde únicamente a estas preguntas:\n"
        "1. ¿Qué información relevante sobre el tema falta en estos apuntes?\n"
        "2. ¿Detectas contradicciones o incoherencias importantes?\n"
        "3. Si tuvieras que ampliar estos apuntes, ¿qué subtemas incluirías para que fueran más completos?\n"
        "NO inventes información nueva, solo señala lo que falta o no se explica.\n"
        "Si todo está completo, di claramente: 'No se detectan lagunas relevantes.'\n\n"
        f"Tema: {tema}\n\n"
        "Texto de los apuntes:\n"
        f"{contexto}\n"
    )
    respuesta_llm = modelo_llm.invoke(prompt)
    respuesta_texto = respuesta_llm.content if hasattr(respuesta_llm, "content") else respuesta_llm

    try:
        resultado = re.search(r'\{.*\}', respuesta_texto, re.DOTALL)
        if resultado:
            informe = json.loads(resultado.group())
        else:
            raise ValueError("No se encontró JSON válido.")
    except Exception as e:
        print("❌ Error al parsear el JSON:", e)
        print("Respuesta bruta:", respuesta_texto)
        informe = None

    return informe

def generar_chunk_expansion_tool(materia, tema, punto, contexto, modelo_llm):
    prompt = (
        f"Estás ayudando a mejorar unos apuntes de {materia}, tema '{tema}'. "
        f"El siguiente punto no está bien cubierto en los apuntes:\n\n"
        f"'{punto}'\n\n"
        f"Este es el texto actual de los apuntes:\n{contexto}\n\n"
        "Genera un texto breve, claro y bien estructurado (máx. 120 palabras) para cubrir este punto. "
        "No repitas el contexto ni hagas introducciones, ve al grano, en el mismo tono que los apuntes. "
        "Si ya está en los apuntes, di: 'Este punto ya está cubierto'."
    )
    respuesta = modelo_llm.invoke(prompt)
    return respuesta.content if hasattr(respuesta, "content") else str(respuesta)

def insertar_chunks_en_vectorstore(nuevos_chunks, materia, tema):
    store = cargar_vectorstore(materia, tema)
    if store is None:
        print("⚠️ No se pudo cargar el vectorstore.")
        return False

    documentos_nuevos = [
        Document(
            page_content=chunk["texto"],
            metadata={"fuente": "expansion_llm", "punto": chunk["punto"]}
        )
        for chunk in nuevos_chunks
    ]

    store.add_documents(documentos_nuevos)

    ruta_guardado = VECTORSTORE_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}"
    store.save_local(str(ruta_guardado))

    print(f"✅ {len(documentos_nuevos)} nuevos chunks insertados en el vectorstore de '{tema}'.")
    return True

def insertar_chunks_en_vectorstore_tool(nuevos_chunks, materia, tema):
    ok = insertar_chunks_en_vectorstore(nuevos_chunks, materia, tema)
    return "Inserción completada." if ok else "Fallo al insertar los chunks."

def enriquecer_apuntes_tool(materia, tema, modelo_llm):
    resultado = analizar_lagunas_en_contexto_tool(materia, tema, modelo_llm)
    contexto = obtener_todo_contexto_vectorstore(materia, tema)

    if not resultado or not contexto:
        return {
            "mensaje": "No se pudo enriquecer los apuntes por falta de información.",
            "chunks_creados": 0,
            "subtemas_agregados": [],
            "detalle": []
        }

    puntos = resultado.get("ausencias", []) + resultado.get("subtemas_recomendados", [])
    nuevos_chunks = []

    for punto in puntos:
        expansion = generar_chunk_expansion_tool(materia, tema, punto, contexto, modelo_llm)
        if expansion and "ya está cubierto" not in expansion.lower():
            nuevos_chunks.append({"punto": punto, "texto": expansion})

    if not nuevos_chunks:
        return {
            "mensaje": "No se generaron nuevos chunks.",
            "chunks_creados": 0,
            "subtemas_agregados": [],
            "detalle": []
        }

    insertar_chunks_en_vectorstore(nuevos_chunks, materia, tema)
    # Estructura de respuesta rica:
    return {
        "mensaje": f"{len(nuevos_chunks)} nuevos chunks añadidos correctamente.",
        "chunks_creados": len(nuevos_chunks),
        "subtemas_agregados": [chunk["punto"] for chunk in nuevos_chunks],
        "detalle": [
            {
                "titulo": chunk["punto"],
                "resumen": chunk["texto"][:200] + "..." if len(chunk["texto"]) > 200 else chunk["texto"]
            }
            for chunk in nuevos_chunks
        ]
    }

def generar_clase_magistral(materia, tema, modelo_llm, tts_func=None):
    """
    Orquesta el proceso de enriquecer apuntes, obtener títulos, generar el texto (y audio) de la clase magistral.
    """
    # 1. Enriquecer apuntes
    resultado_enriquecimiento = enriquecer_apuntes_tool(materia, tema, modelo_llm)
    # 2. Obtener títulos de los chunks
    titulos_unicos = obtener_titulos_vectorstore(materia, tema)
    texto_clase_base = construir_texto_clase_base(titulos_unicos)
    # 3. Crear prompt y generar texto de profesor
    prompt_profesor = crear_prompt_profesor(materia, tema, texto_clase_base)
    texto_profesor = generar_texto_profesor(prompt_profesor, modelo_llm)
    # 4. (Opcional) Audio
    audio_url = tts_func(texto_profesor) if tts_func else None
    # 5. Estructura de respuesta
    return {
        "mensaje": resultado_enriquecimiento["mensaje"],
        "chunks_creados": resultado_enriquecimiento["chunks_creados"],
        "subtemas_agregados": resultado_enriquecimiento["subtemas_agregados"],
        "clase_magistral_texto": texto_profesor,
        "audio_url": audio_url,
        "detalle_chunks": resultado_enriquecimiento.get("detalle", [])
    }