PREGUNTAS_GENERICAS = [
    "explica", "resumen", "resumir", "de qué trata", "introducción",
    "puedes hacer un resumen", "puedes explicarme", "hazme un resumen", "explica este tema", "qué sabes de",
    "resumen de", "en ", "palabras", "hazme un resumen de ", "puedes resumir", "resume en", "resumemelo",
    "podrías resumir", "podrías hacerme un resumen de ", "resumen en"
]
def es_pregunta_generica(pregunta, tema):
    p = pregunta.lower()
    t = tema.lower()
    if t in p:
        return True
    return any(pat in p for pat in PREGUNTAS_GENERICAS)
from fastapi import APIRouter, Query, UploadFile, File, Form, HTTPException
from pathlib import Path
from pydantic import BaseModel
from typing import List
from src.apuntes.scripts.agents.agent_tools import postprocesar_clase_magistral_groq
import os
import requests
from src.config import GROQ_API_KEY
from src.api.schemas import ChatExplicaSimpleRequest, ChatExplicaSimpleResponse, MensajeChat
from src.apuntes.scripts.rag_local import es_pregunta_relevante

from src.services.tutor import (
    responder_pregunta_servicio,
    explicar_como_nino_servicio,
    procesar_apunte_completo,
    evaluar_desarrollo_servicio,
    enriquecer_apuntes_servicio
)

def limpiar_contexto(contexto: str) -> str:
    """
    Elimina frases limitantes o negativas del contexto para que el modelo nunca devuelva
    respuestas tipo 'Lo siento, no hay suficiente información...'.
    """
    frases_prohibidas = [
        "lo siento", "no puedo", "no hay suficiente información",
        "el texto proporcionado", "no se proporciona", "si deseas",
        # "sin embargo", "no cubre todos los aspectos", "no tengo suficiente información",
        "no puedo generar", "no puedo responder", "no puedo ayudarte", "no está disponible"
    ]
    lineas = contexto.split('\n')
    limpias = [
        l for l in lineas
        if not any(f.lower() in l.lower() for f in frases_prohibidas)
    ]
    return '\n'.join(limpias).strip()

router = APIRouter()

# Directorio donde se almacenan los vectorstores
VECTORSTORE_DIR = Path("src/apuntes/rag/vectorstores")

@router.get("/responder_pregunta")
def responder_pregunta(
    materia: str = Query(...),
    tema: str = Query(...),
    pregunta: str = Query(...)
):
    """
    Endpoint para responder una pregunta usando RAG y Groq.
    """
    return {"respuesta": responder_pregunta_servicio(materia, tema, pregunta)}


@router.get("/explicar_como_nino")
def explicar_como_nino(
    materia: str = Query(...),
    tema: str = Query(...)
):
    """
    Endpoint para explicar un tema como si se tuviera 12 años.
    """
    return {"explicacion": explicar_como_nino_servicio(materia, tema)}


@router.post("/procesar_apunte")
async def procesar_apunte(
    materia: str = Form(...),
    tema: str = Form(...),
    archivo: UploadFile = File(...)
):
    """
    Procesa un nuevo apunte: analiza, trocea y actualiza vectorstore.
    """
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    archivo_destino = uploads_dir / archivo.filename

    with open(archivo_destino, "wb") as f:
        contenido = await archivo.read()
        f.write(contenido)

    mensaje = procesar_apunte_completo(materia, tema, archivo.filename)
    return {"mensaje": mensaje}


# Modelo para evaluación de respuestas
class DesarrolloInput(BaseModel):
    materia: str
    tema: str  # nombre del tema en los apuntes
    titulo_tema: str  # título del desarrollo hecho por el alumno
    desarrollo: str   # texto redactado por el estudiante

@router.post("/evaluar_desarrollo")
def evaluar_desarrollo(payload: DesarrolloInput):
    """
    Evalúa un desarrollo completo sobre un tema, comparándolo con los apuntes del alumno.
    """
    try:
        resultado = evaluar_desarrollo_servicio(
            materia=payload.materia,
            tema=payload.tema,
            titulo_tema=payload.titulo_tema,
            desarrollo=payload.desarrollo
        )
        return {"evaluacion": resultado}
    except ValueError as e:
        print(f"[ERROR evaluar_desarrollo] {e}")
        raise HTTPException(status_code=400, detail="El desarrollo no es válido o está incompleto.")


@router.get("/materias", response_model=List[str])
def obtener_materias():
    """
    Devuelve el listado de materias (carpetas con vectorstores).
    """
    materias = {
        nombre.split("__")[0]
        for nombre in [f.name for f in VECTORSTORE_DIR.iterdir() if f.is_dir()]
        if "__" in nombre
    }
    return sorted(materias)


@router.get("/temas", response_model=List[str])
def obtener_temas(materia: str):
    """
    Devuelve el listado de temas disponibles para una materia concreta.
    """
    temas = [
        f.name.split("__")[1].replace("_", " ").capitalize()
        for f in VECTORSTORE_DIR.iterdir()
        if f.is_dir() and f.name.startswith(f"{materia}__")
    ]
    return sorted(temas)


@router.get("/debug/vectorstores", response_model=List[str])
def listar_vectorstores():
    """
    Endpoint de depuración para listar los nombres de los vectorstores existentes.
    """
    return sorted([f.name for f in VECTORSTORE_DIR.iterdir() if f.is_dir()])


from src.apuntes.scripts.agents.agente_creador_clase_magistral import (
    agente_clase_magistral,
    insertar_clase_magistral_en_json
)

# Importar la función limpiar_apuntes
from src.apuntes.scripts.agents.limpiar_apuntes import limpiar_apuntes

@router.post("/enriquecer_apuntes")
def enriquecer_apuntes(materia: str, tema: str):
    try:
        print(f"[API] Enriqueciendo apuntes para materia='{materia}', tema='{tema}'")
        resultado = enriquecer_apuntes_servicio(materia, tema)

        # --- VALIDACIÓN DEFENSIVA PARA SIEMPRE DEVOLVER LA ESTRUCTURA ESPERADA ---
        if not isinstance(resultado, dict):
            resultado = {"mensaje": {"chunks_creados": 0, "subtemas_agregados": [], "detalle": []}, "ya_analizado": False}
        elif "mensaje" not in resultado or not isinstance(resultado["mensaje"], dict):
            resultado["mensaje"] = {"chunks_creados": 0, "subtemas_agregados": [], "detalle": []}
        if "ya_analizado" not in resultado:
            resultado["ya_analizado"] = False
        # -------------------------------------------------------------------------

        print(f"[API] Resultado enriquecimiento: {resultado.get('mensaje', 'OK')}")
        return resultado

    except HTTPException as e:
        print(f"[API ERROR] HTTPException enriqueciendo apuntes: {e.detail}")
        raise e
    except Exception as e:
        print(f"[API ERROR] Error inesperado enriqueciendo apuntes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inesperado al enriquecer los apuntes.")


from fastapi import HTTPException

# Nuevo endpoint para generar clase magistral
# --- Función auxiliar para construir respuestas de error robustas y mantener historial ---
def construir_respuesta_error(req, mensaje):
    """Crea la respuesta de error con el historial actualizado."""
    historial_actualizado = req.historial + [MensajeChat(role="tutor", content=mensaje)]
    return ChatExplicaSimpleResponse(
        respuesta=mensaje,
        historial=historial_actualizado
    )


@router.post("/chat_explica_simple", response_model=ChatExplicaSimpleResponse)
def chat_explica_simple(req: ChatExplicaSimpleRequest):
    # ATENCIÓN: Esta función requiere una futura refactorización/modularización por su tamaño y complejidad actuales.
    # Se recomienda extraer lógica en helpers y manejar casos de error de manera aún más granular en el futuro.

    pregunta_actual = req.historial[-1].content if req.historial else ""

    # Comprobar si la pregunta es relevante respecto a los apuntes
    pregunta_relevante = False
    if req.materia and req.tema and pregunta_actual:
        try:
            pregunta_relevante = es_pregunta_relevante(req.materia, req.tema, pregunta_actual)
        except Exception as e:
            print(f"[RAG Chat] Error comprobando relevancia de la pregunta: {e}")
            # Consideramos irrelevante si hay error, pero devolvemos mensaje claro después
            pregunta_relevante = False

    if not pregunta_relevante:
        # Segunda pasada: ¿Es una pregunta genérica sobre el tema?
        if req.tema and es_pregunta_generica(pregunta_actual, req.tema):
            # Forzamos el contexto: cogemos TODOS los apuntes del tema usando el propio tema como pregunta
            try:
                contexto = responder_pregunta_servicio(req.materia, req.tema, req.tema)
                if isinstance(contexto, dict) and "respuesta" in contexto:
                    contexto = contexto["respuesta"]
            except Exception as e:
                print(f"[RAG Chat] Error en segunda pasada contexto: {e}")
                return construir_respuesta_error(
                    req,
                    "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
                )
            contexto = limpiar_contexto(contexto)

            if contexto.strip():
                # Repetimos el flujo de respuesta normal, pero con el contexto completo
                system_prompt = (
                    "Eres un tutor académico. Cuando respondas, separa SIEMPRE la respuesta en dos bloques diferenciados:\n"
                    "1. Primero, incluye SOLO la información que aparece en los apuntes, integrándola de manera natural en el texto y SIN poner ningún título ni etiqueta.\n"
                    "2. Después, si necesitas completar la respuesta con tu conocimiento general o la pregunta pide una extensión que no puedes cubrir, añade al final un párrafo que empiece en negrita por '**Ampliación generada por la IA:**', y explica qué parte no aparece en los apuntes o si la extensión de la respuesta está limitada por el contexto proporcionado.\n"
                    "Si la extensión solicitada es mayor que el contexto disponible, responde lo más completo posible y explica en la ampliación que la extensión se ha limitado por la información de los apuntes.\n"
                    "Nunca inventes ni alteres datos en la primera parte. Si falta información, añade solo conocimiento bien fundamentado en la segunda.\n"
                    "\nContexto de los apuntes:\n"
                    f"{contexto}\n"
                )
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": pregunta_actual}
                ]
                try:
                    headers = {
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    }
                    data = {
                        "model": "llama3-70b-8192",
                        "messages": messages,
                        "max_tokens": 500,
                        "temperature": 0.7
                    }
                    print("Payload enviado a Groq (segunda pasada):", data)
                    try:
                        response = requests.post(
                            "https://api.groq.com/openai/v1/chat/completions",
                            headers=headers,
                            json=data,
                            timeout=60
                        )
                        response.raise_for_status()
                        result = response.json()
                        respuesta = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                    except requests.exceptions.RequestException as e:
                        print(f"[ERROR Groq segunda pasada][RequestException] {e}")
                        return construir_respuesta_error(
                            req,
                            "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
                        )
                    except Exception as e:
                        print(f"[ERROR Groq segunda pasada][General] {e}")
                        return construir_respuesta_error(
                            req,
                            "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
                        )
                except Exception as e:
                    print(f"[ERROR Groq segunda pasada][Outer] {e}")
                    return construir_respuesta_error(
                        req,
                        "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
                    )
                if not respuesta:
                    return construir_respuesta_error(
                        req,
                        "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
                    )
                historial_actualizado = req.historial + [MensajeChat(role="tutor", content=respuesta)]
                return ChatExplicaSimpleResponse(
                    respuesta=respuesta,
                    historial=historial_actualizado
                )
            # Si no hay contexto, es como si no hubiera información suficiente
            return construir_respuesta_error(
                req,
                "Lo siento, no puedo responder a esa pregunta porque no está en tus apuntes. Por favor, pregunta algo sobre el tema que tienes en tus apuntes."
            )
        # Si no pasa la segunda pasada...
        return construir_respuesta_error(
            req,
            "Lo siento, no puedo responder a preguntas fuera del contexto de tus apuntes. Por favor, haz preguntas relacionadas con tus apuntes para obtener la mejor ayuda."
        )
    else:
        contexto = ""
        if req.materia and req.tema and pregunta_actual:
            try:
                contexto = responder_pregunta_servicio(req.materia, req.tema, pregunta_actual)
                if isinstance(contexto, dict) and "respuesta" in contexto:
                    contexto = contexto["respuesta"]
            except Exception as e:
                print(f"[RAG Chat] Error recuperando contexto: {e}")
                return construir_respuesta_error(
                    req,
                    "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
                )
            contexto = limpiar_contexto(contexto)

        if not contexto.strip():
            return construir_respuesta_error(
                req,
                "Lo siento, no puedo responder a esa pregunta porque no está en tus apuntes. Por favor, pregunta algo sobre el tema que tienes en tus apuntes."
            )

        # Preparar system_prompt solo si hay contexto relevante
        system_prompt = (
            "Eres un tutor académico. Cuando respondas, separa SIEMPRE la respuesta en dos bloques diferenciados:\n"
            "1. Primero, incluye SOLO la información que aparece en los apuntes, integrándola de manera natural en el texto y SIN poner ningún título ni etiqueta.\n"
            "2. Después, si necesitas completar la respuesta con tu conocimiento general o la pregunta pide una extensión que no puedes cubrir, añade al final un párrafo que empiece en negrita por '**Ampliación generada por la IA:**', y explica qué parte no aparece en los apuntes o si la extensión de la respuesta está limitada por el contexto proporcionado.\n"
            "Si la extensión solicitada es mayor que el contexto disponible, responde lo más completo posible y explica en la ampliación que la extensión se ha limitado por la información de los apuntes.\n"
            "Nunca inventes ni alteres datos en la primera parte. Si falta información, añade solo conocimiento bien fundamentado en la segunda.\n"
            "\nContexto de los apuntes:\n"
            f"{contexto}\n"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pregunta_actual}
        ]
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "llama3-70b-8192",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            print("Payload enviado a Groq:", data)
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                respuesta = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            except requests.exceptions.RequestException as e:
                print(f"[ERROR Groq][RequestException] {e}")
                return construir_respuesta_error(
                    req,
                    "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
                )
            except Exception as e:
                print(f"[ERROR Groq][General] {e}")
                return construir_respuesta_error(
                    req,
                    "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
                )
        except Exception as e:
            print(f"[ERROR Groq][Outer] {e}")
            return construir_respuesta_error(
                req,
                "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
            )
        if not respuesta:
            return construir_respuesta_error(
                req,
                "El sistema está teniendo problemas para procesar tu pregunta. Por favor, intenta de nuevo en unos segundos."
            )
        historial_actualizado = req.historial + [MensajeChat(role="tutor", content=respuesta)]
        return ChatExplicaSimpleResponse(
            respuesta=respuesta,
            historial=historial_actualizado
        )