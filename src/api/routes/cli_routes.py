from fastapi import APIRouter, Query
from src.services.tutor import (
    responder_pregunta_servicio,
    explicar_como_nino_servicio,
    procesar_apunte_completo
)

router = APIRouter()

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
def procesar_apunte(
    materia: str = Query(...),
    tema: str = Query(...),
    archivo: str = Query(...)
):
    """
    Procesa un nuevo apunte: analiza, trocea y actualiza vectorstore.
    """
    mensaje = procesar_apunte_completo(materia, tema, archivo)
    return {"mensaje": mensaje}