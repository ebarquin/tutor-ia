from pathlib import Path
from datetime import datetime
import shutil
from src.config import OPENAI_API_KEY


# --- tiktoken import para contar tokens ---
try:
    import tiktoken
except ImportError:
    tiktoken = None
from src.apuntes.scripts.rag_local import (
    obtener_contexto,
    responder_con_groq,
    cargar_vectorstore   # <- 🔧 importante para evaluación
    # client  # Ya no importamos client global, lo gestionamos aquí según modelo
)

from src.apuntes.scripts.analizar_apuntes import analizar
from src.apuntes.scripts.crear_vectorstore import crear_vectorstore
from src.apuntes.scripts.actualizar_materias import cargar_base, guardar_base
from langchain_openai import ChatOpenAI
import os
import re
from src.config import GROQ_API_KEY


"""
tutor.py - Lógica de negocio centralizada para Tutor-IA

Este módulo define las funciones de alto nivel para la gestión de apuntes, respuestas,
explicaciones y evaluaciones en Tutor-IA. Toda la lógica de negocio se centraliza aquí, 
de forma que tanto la API (FastAPI) como la CLI (línea de comandos) llaman a estas funciones 
de servicio para garantizar consistencia y evitar duplicidades. 

Si necesitas modificar cómo se responde a una pregunta, se procesa un apunte, o se evalúa 
un desarrollo, hazlo en este archivo: el cambio se aplicará automáticamente a todos los 
puntos de entrada (web y CLI).
"""

# --- Setup explícito del cliente de OpenAI ---
import openai

# Obtén la API Key de OpenAI desde variable de entorno o config
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurada en el entorno.")

# --- Configuración de modelo para evaluación ---
# Puedes cambiar a "gpt-4o" si tienes acceso, o cualquier modelo GPT oficial de OpenAI habilitado para tu cuenta.
MODELO_EVALUACION = "gpt-3.5-turbo-1106"

# --- Función auxiliar para contar tokens ---
def contar_tokens(texto):
    if tiktoken is None:
        return len(texto) // 4  # Aproximación muy grosera
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(texto))

# --- Función para obtener cliente adecuado según modelo ---
def get_chat_client(model_name: str):
    """Devuelve el cliente correcto según el modelo solicitado."""
    if model_name.startswith("gpt-"):
        # Cliente OpenAI oficial
        return openai.OpenAI(api_key=OPENAI_API_KEY)
    else:
        # Para Groq u otros modelos, importar y crear el cliente aquí si es necesario
        # Pero para evaluación, solo se permite OpenAI
        raise ValueError(f"Modelo {model_name} no soportado para evaluación, debe ser gpt-*")

def normalizar_concepto(concepto: str) -> str:
    # Normaliza quitando puntuación, números y espacios, y pasando a minúsculas para evitar duplicados
    return re.sub(r'[\s\.\,\-\_\(\)\[\]\{\}0-9]+', '', concepto.lower())

def doble_validacion_conceptos(conceptos_nocubiertos, desarrollo):
    """
    Doble validación de conceptos no cubiertos usando OpenAI (nunca Groq).
    """
    conceptos_validados = {}
    chat_client = get_chat_client(MODELO_EVALUACION)
    for concepto in conceptos_nocubiertos:
        mini_prompt = f"""
¿El siguiente desarrollo trata (aunque sea de forma indirecta) el concepto '{concepto}'? 
Responde SÍ si aparece, aunque sea con otras palabras, y explica brevemente dónde. Si no, responde NO.
Desarrollo:
\"\"\"
{desarrollo}
\"\"\"
"""
        response = chat_client.chat.completions.create(
            model=MODELO_EVALUACION,
            messages=[{"role": "user", "content": mini_prompt}]
        )
        answer = response.choices[0].message.content.strip().lower()
        if answer.startswith("sí") or answer.startswith("si"):
            conceptos_validados[concepto] = "✔️"
        else:
            conceptos_validados[concepto] = "❌"
    return conceptos_validados

def limpiar_texto_chunk(chunk: str) -> str:
    # Elimina numeración típica al principio de línea (1., 1.1, 1), guiones, etc.
    chunk = re.sub(r'^\s*[\d\-\.]+(\)|\.)?\s+', '', chunk, flags=re.MULTILINE)
    # Elimina títulos en mayúsculas (habituales en apuntes, p.ej. "INTRODUCCIÓN", "RESUMEN")
    chunk = re.sub(r'^[A-ZÁÉÍÓÚÜÑ\s]{4,}$', '', chunk, flags=re.MULTILINE)
    # Sustituye saltos de línea múltiples por uno solo
    chunk = re.sub(r'\n+', '\n', chunk)
    # Quita espacios al principio y final
    chunk = chunk.strip()
    # Elimina líneas vacías
    chunk = '\n'.join([line for line in chunk.splitlines() if line.strip()])
    return chunk

# ---------- CORE DE FUNCIONES ----------

def generar_respuesta(materia, tema, pregunta):
    contexto, advertencia = obtener_contexto(materia, tema, pregunta)
    if advertencia:
        return None, advertencia
    return responder_con_groq(materia, pregunta, contexto), None


def explicar_como_nino(materia, tema):
    contexto, advertencia = obtener_contexto(materia, tema, f"Resumen claro")
    if advertencia:
        return None, advertencia

    prompt = (
        "Explica de forma clara, sencilla y directa el siguiente contenido, "
        "sin usar frases como 'estos apuntes', 'este texto', 'este documento' o similares. "
        "Empieza con la información relevante, usa frases cortas y no añadas saludos ni introducciones. "
        "Organiza la explicación con buena estructura y ejemplos cuando sean útiles. "
        "No añadas información externa ni te inventes nada. Limita la explicación a 500 palabras.\n\n"
        "Contenido de los apuntes:\n"
        f"{contexto}\n\n"
        "Explica lo esencial de estos apuntes para que cualquiera lo entienda fácilmente."
    )

    return responder_con_groq(materia, "Explica claramente el contenido de estos apuntes", prompt), None

def subir_y_procesar_apunte(materia, tema, archivo):
    base = cargar_base()

    if materia not in base:
        base[materia] = {}
    if tema not in base[materia]:
        base[materia][tema] = {"versiones": []}

    archivo_origen = Path(archivo)
    if not archivo_origen.exists():
        posible = Path("uploads") / archivo
        if posible.exists():
            archivo_origen = posible
        else:
            return None, f"❌ El archivo '{archivo}' no existe ni en la ruta dada ni en 'uploads/'."

    fecha = datetime.today().strftime("%Y-%m-%d")
    nombre_base = archivo_origen.stem
    nuevo_nombre = f"{nombre_base}_v{len(base[materia][tema]['versiones']) + 1}.pdf"

    destino = Path("data/pdf") / nuevo_nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(archivo_origen, destino)

    base[materia][tema]["versiones"].append({
        "origen": archivo_origen.name,
        "archivo": nuevo_nombre,
        "fecha": fecha
    })
    guardar_base(base)

    analizar(materia=materia, tema=tema)
    crear_vectorstore(materia=materia, tema=tema)

    return nuevo_nombre, None


# ---------- FUNCIONES SERVICIO PARA API ----------

def responder_pregunta_servicio(materia: str, tema: str, pregunta: str) -> str:
    respuesta, advertencia = generar_respuesta(materia, tema, pregunta)
    if advertencia:
        raise ValueError(advertencia)
    return respuesta


def explicar_como_nino_servicio(materia: str, tema: str) -> str:
    respuesta, advertencia = explicar_como_nino(materia, tema)
    if advertencia:
        raise ValueError(advertencia)
    return respuesta


def procesar_apunte_completo(materia: str, tema: str, archivo: str) -> str:
    nombre, error = subir_y_procesar_apunte(materia, tema, archivo)
    if error:
        raise ValueError(error)
    return f"✅ Apunte '{nombre}' procesado correctamente para {materia} / {tema}."


# Pipeline en cadena por bloques para evaluar desarrollos:
# Esta función divide los apuntes en bloques manejables, resume cada bloque para extraer la información esencial,
# y luego utiliza estos resúmenes para evaluar globalmente el desarrollo del estudiante.
# Esto permite manejar grandes volúmenes de texto sin exceder límites de tokens,
# mejora la coherencia y precisión de la evaluación, y evita perder contexto importante.

def evaluar_desarrollo_servicio(materia: str, tema: str, titulo_tema: str, desarrollo: str) -> str:
    """
    Evaluación de desarrollo: usa SIEMPRE OpenAI para extracción de conceptos y corrección.
    """
    db = cargar_vectorstore(materia, tema)
    if db is None:
        raise ValueError(f"❌ No se encontró el vectorstore para {materia} / {tema}.")

    docs_similares = db.similarity_search("", k=1000)
    chunks_limpios = [limpiar_texto_chunk(doc.page_content) for doc in docs_similares]

    max_tokens_bloque = 2400
    max_chars_bloque = max_tokens_bloque * 4
    bloques = []
    temp_bloque = ""
    temp_chars = 0
    for chunk in chunks_limpios:
        chunk_len = len(chunk)
        if temp_chars + chunk_len < max_chars_bloque:
            temp_bloque += chunk + "\n"
            temp_chars += chunk_len
        else:
            if temp_bloque:
                bloques.append(temp_bloque)
            temp_bloque = chunk + "\n"
            temp_chars = chunk_len
    if temp_bloque:
        bloques.append(temp_bloque)

    # --- SOLO OpenAI para extracción de conceptos clave por bloque ---
    chat_client = get_chat_client(MODELO_EVALUACION)
    conceptos_por_bloque = []
    for bloque in bloques:
        conceptos_prompt = (
            f"Lee el siguiente texto y extrae SOLO los conceptos clave necesarios para corregir un desarrollo sobre el tema '{titulo_tema}'. "
            "No resumas, no expliques, solo una lista (1 concepto por línea, sin descripciones):\n\n"
            f"{bloque}\n\n"
            "Lista de conceptos clave:"
        )
        conceptos = chat_client.chat.completions.create(
            model=MODELO_EVALUACION,
            messages=[{"role": "user", "content": conceptos_prompt}]
        ).choices[0].message.content
        conceptos_por_bloque.append(conceptos)

    # Fusionar listas y eliminar duplicados usando normalización, pero conservar forma original
    conceptos_dict = {}
    for lista in conceptos_por_bloque:
        for linea in lista.splitlines():
            concepto_original = linea.strip(" .•-*1234567890")
            if concepto_original:
                clave = normalizar_concepto(concepto_original)
                if clave and clave not in conceptos_dict:
                    conceptos_dict[clave] = concepto_original
    lista_final = sorted(conceptos_dict.values(), key=lambda x: x.lower())

    conceptos_texto = "\n".join(lista_final)
    prompt_final = f"""
Corrige el desarrollo completo de un estudiante sobre el tema "{titulo_tema}" en {materia}.

Lista de conceptos clave extraídos de los apuntes originales:
\"\"\"
{conceptos_texto}
\"\"\"

Desarrollo redactado por el estudiante:
\"\"\"
{desarrollo}
\"\"\"

Instrucciones para la evaluación (sigue el formato exacto):

- Enumera cada concepto en una lista en Markdown, en una sola línea, usando el formato:  
  - concepto: ✔️  (si está correctamente explicado)
  - concepto: ❌  (si falta o está incorrecto)
- No agrupes conceptos ni los pongas seguidos en párrafos. SOLO una lista, una línea por concepto, con guion delante.
- Al final de la lista, indica solo la nota final sobre 10, SIN poner el porcentaje de cobertura ni fórmulas.
- Si la cobertura es del 80% o más, la nota es 10/10. Si es menos, disminuye progresivamente en función de los conceptos cubiertos.
- Da una breve justificación y consejos SOLO sobre los conceptos marcados con ❌. No repitas los conceptos cubiertos ni los aciertos.
- No añadas encabezados, títulos ni explicaciones adicionales. Solo la lista, la nota y la justificación/consejos.
- Responde en español.

Ejemplo de formato esperado:

- ataque a pearl harbor: ✔️
- banco internacional de reconstrucción y desarrollo: ✔️
- batalla de inglaterra: ✔️
- bombardeo atómico de hiroshima y nagasaki: ❌
...
Nota final: 9/10

Justificación y consejos: Faltan algunos conceptos como 'bombardeo atómico de hiroshima y nagasaki'. Añádelos y repasa para mejorar tu nota.
"""
    response = chat_client.chat.completions.create(
        model=MODELO_EVALUACION,
        messages=[{"role": "user", "content": prompt_final}]
    )
    response_text = response.choices[0].message.content

    # --- Doble validación de conceptos no cubiertos ---
    import re
    conceptos_list = []
    for line in response_text.splitlines():
        match = re.match(r"^\s*-\s*(.+?):\s*(✔️|❌)", line)
        if match:
            concepto, estado = match.groups()
            conceptos_list.append((concepto.strip(), estado))

    conceptos_nocubiertos = [c for c, estado in conceptos_list if estado == "❌"]

    if conceptos_nocubiertos:
        resultados_validados = doble_validacion_conceptos(conceptos_nocubiertos, desarrollo)
        conceptos_list = [(c, resultados_validados.get(c, e)) if e == "❌" else (c, e) for c, e in conceptos_list]

    # Recalcula la nota tras la validación
    total = len(conceptos_list)
    cubiertos = sum(1 for _, estado in conceptos_list if estado == "✔️")
    cobertura = cubiertos / total if total else 0

    if cobertura >= 0.8:
        nota = 10
    else:
        nota = round(cobertura * 10, 1)

    # Formato final
    lista_md = "\n".join([f"- {c}: {e}" for c, e in conceptos_list])
    # Extrae solo los conceptos realmente NO cubiertos para la justificación
    conceptos_faltan = [c for c, e in conceptos_list if e == "❌"]
    consejos = ""
    if conceptos_faltan:
        consejos = f"Faltan conceptos como {', '.join([repr(c) for c in conceptos_faltan])}. Añádelos y repasa para mejorar tu nota."
    else:
        consejos = "¡Excelente! Has cubierto todos los conceptos clave del tema."

    salida = f"{lista_md}\nNota final: {nota}/10\n\nJustificación y consejos: {consejos}"
    return salida

# --- BLOQUE QUE USA GROQ para generación general (resúmenes, expansión, etc.) ---
def enriquecer_apuntes_servicio(materia, tema):
    store = cargar_vectorstore(materia, tema)
    docs = store.similarity_search("", k=1000)
    chunks_expansion = [doc for doc in docs if doc.metadata.get("fuente") == "expansion_llm"]
    llm = ChatOpenAI(
        api_key= GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        model="llama3-70b-8192",
        temperature=0.2
    )

    if chunks_expansion:
        return {
            "ya_analizado": True,
            "mensaje": f"Ya se han generado {len(chunks_expansion)} chunks de expansión por LLM para este tema.",
            "chunks_creados": len(chunks_expansion),
            "detalle": [
                {
                    "contenido": doc.page_content,
                    "metadata": doc.metadata
                } for doc in chunks_expansion
            ]
        }
    
    resultado = enriquecer_apuntes_tool(materia, tema, llm)
    return {
        "ya_analizado": False,
        **resultado
    }