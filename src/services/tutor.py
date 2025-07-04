# src/services/tutor.py

from pathlib import Path
from datetime import datetime
import shutil
from src.apuntes.scripts.rag_local import (
    obtener_contexto,
    responder_con_groq,
    cargar_vectorstore,   # <- 🔧 importante para evaluación
    client                # <- 🔧 cliente de Groq u OpenAI
)

from src.apuntes.scripts.analizar_apuntes import analizar
from src.apuntes.scripts.crear_vectorstore import crear_vectorstore
from src.apuntes.scripts.actualizar_materias import cargar_base, guardar_base
from langchain_openai import ChatOpenAI
import os

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


def evaluar_desarrollo_servicio(materia: str, tema: str, titulo_tema: str, desarrollo: str) -> str:
    db = cargar_vectorstore(materia, tema)
    if db is None:
        raise ValueError(f"❌ No se encontró el vectorstore para {materia} / {tema}.")

    docs_similares = db.similarity_search(titulo_tema, k=4)
    contexto = "\n".join(doc.page_content for doc in docs_similares)

    prompt = f"""
Eres un profesor experto en {materia}, corrigiendo un desarrollo completo del estudiante sobre el tema: "{titulo_tema}".

Este desarrollo debe basarse únicamente en los siguientes apuntes:
\"\"\"
{contexto}
\"\"\"

Desarrollo redactado por el estudiante:
\"\"\"
{desarrollo}
\"\"\"

Corrige el desarrollo siguiendo estos puntos:
1. ¿Qué partes están correctamente explicadas según los apuntes?
2. ¿Qué errores o imprecisiones se detectan?
3. ¿Qué información importante falta según el contexto?
4. ¿Qué consejo le darías para mejorar?
5. Asigna una nota final del 0 al 10, solo en base a los apuntes procesados.

No añadas información externa. Tu corrección debe ser clara, objetiva y útil para mejorar su aprendizaje.
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192", 
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def enriquecer_apuntes_servicio(materia, tema):
    store = cargar_vectorstore(materia, tema)
    docs = store.similarity_search("", k=1000)
    chunks_expansion = [doc for doc in docs if doc.metadata.get("fuente") == "expansion_llm"]
    llm = ChatOpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
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