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


# ---------- CORE DE FUNCIONES ----------

def generar_respuesta(materia, tema, pregunta):
    contexto, advertencia = obtener_contexto(materia, tema, pregunta)
    if advertencia:
        return None, advertencia
    return responder_con_groq(materia, pregunta, contexto), None


def explicar_como_nino(materia, tema):
    pregunta_sintetica = f"Explícame el tema '{tema}' de la materia '{materia}' como si tuviera 12 años"
    contexto, advertencia = obtener_contexto(materia, tema, pregunta_sintetica)
    if advertencia:
        return None, advertencia

    prompt = (
        f"Explica el siguiente tema de manera clara y sencilla, evitando tecnicismos innecesarios. "
        f"No uses un tono infantil ni exageradamente académico. Imagina que estás escribiendo para alguien "
        f"que no sabe mucho del tema, pero quiere entenderlo bien.\n\n"
        f"Organiza la explicación con buena estructura, frases directas y ejemplos cuando sean útiles. "
        f"No introduzcas saludos ni metáforas innecesarias. Limita la respuesta a un máximo de 200 palabras.\n\n"
        f"Tema: {tema} ({materia})\n\n"
        f"Contexto disponible:\n{contexto}\n\n"
        f"Ahora, genera una explicación clara, precisa y útil para cualquier lector interesado. "
        f"Recuerda: no más de 200 palabras."
    )

    return responder_con_groq(materia, pregunta_sintetica, prompt), None


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