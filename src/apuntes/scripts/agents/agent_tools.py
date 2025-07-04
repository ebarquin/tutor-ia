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

def dividir_en_bloques(lista, tamano):
    for i in range(0, len(lista), tamano):
        yield lista[i:i+tamano]

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
    return "\n".join(f"- {t}" for t in titulos if t)

def detectar_subtemas_pobres(materia, tema, min_longitud=80):
    store = cargar_vectorstore(materia, tema)
    if not store:
        return []
    docs = store.similarity_search("", k=50)
    subtemas_pobres = []
    for doc in docs:
        texto = doc.page_content.strip()
        titulo = doc.metadata.get("punto") or doc.metadata.get("titulo") or ""
        if titulo and len(texto.split()) < min_longitud:
            subtemas_pobres.append({"titulo": titulo, "longitud": len(texto.split())})
    return subtemas_pobres

def crear_prompt_profesor(materia: str, tema: str, texto_clase_base: str):
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
    return texto_profesor

def tts_func(
    texto,
    carpeta_destino="audios",
    voz_id="6xftrpatV0jGmFHxDjUv",
    modelo="eleven_multilingual_v2"
):
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

# LLMs
llm_groq = ChatOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama3-70b-8192",
    temperature=0.2
)

llm_gpt35 = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo",
    temperature=0.2
)

# --- FUNCIONES DE DESARROLLO Y EVALUACIÓN DE SUBTEMAS ---


def generar_desarrollo_subtema_groq(titulo, contexto_base, prompt_personalizado=None):
    """
    Genera el desarrollo del subtema usando Groq (Llama3-70B). Usa prompt estándar o personalizado.
    """
    if prompt_personalizado:
        prompt = prompt_personalizado
    else:
        prompt = (
            f"Eres un profesor universitario preparando una clase magistral.\n"
            f"Desarrolla el siguiente subtema de forma detallada y clara, orientada a estudiantes universitarios.\n"
            f"Usa un lenguaje académico, explicaciones claras y ofrece contexto suficiente.\n\n"
            f"Título del subtema:\n\"{titulo}\"\n\nContexto base del subtema:\n\"{contexto_base}\"\n\nDesarrollo del subtema:"
        )
    respuesta = llm_groq.invoke(prompt)
    return respuesta.content.strip()

def generar_desarrollo_subtema_gpt35(titulo, contexto_base, prompt_personalizado=None):
    """
    Genera el desarrollo del subtema usando GPT-3.5 Turbo. Usa prompt estándar o personalizado.
    """
    if prompt_personalizado:
        prompt = prompt_personalizado
    else:
        prompt = (
            f"Eres un profesor universitario preparando una clase magistral.\n"
            f"Desarrolla el siguiente subtema de forma detallada y clara, orientada a estudiantes universitarios.\n"
            f"Usa un lenguaje académico, explicaciones claras y ofrece contexto suficiente.\n\n"
            f"Título del subtema:\n\"{titulo}\"\n\nContexto base del subtema:\n\"{contexto_base}\"\n\nDesarrollo del subtema:"
        )
    respuesta = llm_gpt35.invoke(prompt)
    return respuesta.content.strip()

def generar_prompt_especifico_groq(titulo, contexto_base):
    """
    Genera un prompt específico con Groq para mejorar el desarrollo de un subtema concreto.
    """
    prompt = (
        f"El desarrollo generado para el siguiente subtema ha sido considerado insuficiente.\n"
        f"Crea un prompt muy específico y eficaz que pueda usarse con un modelo LLM para obtener una mejor versión.\n\n"
        f"Título del subtema:\n\"{titulo}\"\n\nContexto base:\n\"{contexto_base}\"\n\n"
        "Genera solo el prompt, sin introducciones ni explicaciones adicionales."
    )
    respuesta = llm_groq.invoke(prompt)
    return respuesta.content.strip()

def evaluar_calidad_desarrollo(titulo, desarrollo):
    """
    Evalúa si el desarrollo generado de un subtema es rico o pobre.
    Devuelve 'rico' o 'pobre'. Si no es ninguno, lanza error.
    """
    prompt = (
        f"Actúa como evaluador de apuntes universitarios. Evalúa si el siguiente desarrollo de un subtema "
        f"es suficientemente profundo, estructurado y explicativo como para formar parte de una clase magistral.\n\n"
        f"Título del subtema:\n\"{titulo}\"\n\nDesarrollo del subtema:\n{desarrollo}\n\n"
        "Tu evaluación debe ser solo una palabra: rico o pobre."
    )
    respuesta = llm_groq.invoke(prompt)
    salida = respuesta.content if hasattr(respuesta, "content") else str(respuesta)
    salida = salida.strip().lower().replace('.', '').replace(':', '').replace('¿', '').replace('?', '').replace('¡', '').replace('!', '')
    if "rico" in salida:
        return "rico"
    elif "pobre" in salida:
        return "pobre"
    else:
        raise ValueError(f"La evaluación del LLM no ha devuelto ni 'rico' ni 'pobre': {salida}")

def generar_desarrollo_orquestado(titulo, contexto_base):
    """
    Nuevo pipeline:
      1. Groq (prompt general)
      2. Si pobre, Groq con prompt específico
      3. Si pobre, GPT3.5 con prompt específico
    """
    # Paso 1: Groq (genérico)
    desarrollo_1 = generar_desarrollo_subtema_groq(titulo, contexto_base)
    try:
        evaluacion_1 = evaluar_calidad_desarrollo(titulo, desarrollo_1)
    except Exception as e:
        print(f"⚠️ Error evaluando calidad Groq: {e}")
        evaluacion_1 = "pobre"
    if evaluacion_1 == "rico":
        return desarrollo_1

    # Paso 2: Groq con prompt específico
    prompt_especifico = generar_prompt_especifico_groq(titulo, contexto_base)
    desarrollo_2 = generar_desarrollo_subtema_groq(titulo, contexto_base, prompt_personalizado=prompt_especifico)
    try:
        evaluacion_2 = evaluar_calidad_desarrollo(titulo, desarrollo_2)
    except Exception as e:
        print(f"⚠️ Error evaluando calidad Groq (prompt específico): {e}")
        evaluacion_2 = "pobre"
    if evaluacion_2 == "rico":
        return desarrollo_2

    # Paso 3: GPT3.5 Turbo con prompt específico
    desarrollo_3 = generar_desarrollo_subtema_gpt35(titulo, contexto_base, prompt_personalizado=prompt_especifico)
    # Se devuelve aunque sea pobre (último intento)
    return desarrollo_3

def generar_clase_magistral_avanzada(materia: str, tema: str, max_subtemas: int = 10):
    """
    Orquesta la generación de la clase magistral desarrollando todos los subtemas/títulos principales.
    """
    titulos = obtener_titulos_vectorstore(materia, tema, max_chunks=max_subtemas)
    print(f"Generando desarrollo para {len(titulos)} subtemas...")
    exposiciones = []
    for i, titulo in enumerate(titulos, 1):
        print(f"\n--- [{i}/{len(titulos)}] Desarrollando: {titulo} ---")
        # Puedes obtener el contexto base de cada chunk o un contexto general si lo prefieres
        contexto_base = ""  # O usa el chunk asociado si lo tienes
        desarrollo = generar_desarrollo_orquestado(titulo, contexto_base)
        exposiciones.append(f"### {titulo}\n\n{desarrollo}")
    clase_magistral = "\n\n".join(exposiciones)
    return clase_magistral