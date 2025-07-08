from fastapi import APIRouter, Query, UploadFile, File, Form, HTTPException
from pathlib import Path
from pydantic import BaseModel
from typing import List
from src.apuntes.scripts.agents.agent_tools import postprocesar_clase_magistral_groq
import os
import requests
from src.config import GROQ_API_KEY
from src.api.schemas import ChatExplicaSimpleRequest, ChatExplicaSimpleResponse, MensajeChat

from src.services.tutor import (
    responder_pregunta_servicio,
    explicar_como_nino_servicio,
    procesar_apunte_completo,
    evaluar_desarrollo_servicio,
    enriquecer_apuntes_servicio
)

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
@router.post("/chat_explica_simple", response_model=ChatExplicaSimpleResponse)
def chat_explica_simple(req: ChatExplicaSimpleRequest):
    # Recuperar contexto relevante usando responder_pregunta_servicio
    # Si no hay historial, contexto vacío
    pregunta_actual = req.historial[-1].content if req.historial else ""
    contexto = ""
    if req.materia and req.tema and pregunta_actual:
        try:
            contexto = responder_pregunta_servicio(req.materia, req.tema, pregunta_actual)
            # Si devuelve un dict o similar, asegúrate de coger el string
            if isinstance(contexto, dict) and "respuesta" in contexto:
                contexto = contexto["respuesta"]
        except Exception as e:
            print(f"[RAG Chat] Error recuperando contexto: {e}")
            contexto = ""

    system_prompt = (
        "Eres un tutor académico que explica cualquier tema de forma clara, precisa y adaptada a un estudiante que está empezando. "
        "Si la respuesta puede ser breve, no la extiendas innecesariamente. Si el usuario te pide explícitamente algo especial, adáptate a su petición.\n\n"
        f"Utiliza únicamente la siguiente información de los apuntes para responder:\n{contexto}\n"
    )
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    for mensaje in req.historial:
        role = mensaje.role if mensaje.role in ("system", "user", "assistant") else "assistant"
        messages.append({"role": role, "content": mensaje.content})
    ultima_pregunta = req.historial[-1].content if req.historial else ""
    if ultima_pregunta:
        messages.append({"role": "user", "content": ultima_pregunta})

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
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        respuesta = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

    except Exception as e:
        print(f"[ERROR Groq] {e}")
        respuesta = "Lo siento, no he podido generar una respuesta en este momento."

    historial_actualizado = req.historial + [MensajeChat(role="tutor", content=respuesta)]

    return ChatExplicaSimpleResponse(
        respuesta=respuesta,
        historial=historial_actualizado
    )