from fastapi import APIRouter, Query, UploadFile, File, Form, HTTPException
from pathlib import Path
from pydantic import BaseModel
from typing import List
from src.apuntes.scripts.agents.agent_tools import postprocesar_clase_magistral_groq
import os

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
        raise HTTPException(status_code=400, detail=str(e))


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
    resultado = enriquecer_apuntes_servicio(materia, tema)
    return resultado


from fastapi import HTTPException

# Nuevo endpoint para generar clase magistral
@router.post("/generar_clase_magistral")
def generar_clase_magistral(materia: str, tema: str):
    """
    Genera la clase magistral completa para una materia y tema, y la guarda en el JSON de chunks.
    """
    try:
        print(f"Llamando a agente_clase_magistral para materia={materia}, tema={tema}")
        subtemas = list(agente_clase_magistral(materia, tema))
        if not subtemas:
            raise HTTPException(status_code=404, detail="No se encontraron subtemas para generar la clase magistral.")
        texto_clase = "\n\n".join([s["desarrollo"] for s in subtemas])
        groq_api_key = os.getenv("GROQ_API_KEY")
        texto_clase_limpio = postprocesar_clase_magistral_groq(texto_clase, groq_api_key)
        insertar_clase_magistral_en_json(materia, tema, texto_clase, texto_clase_limpio)
        return {"mensaje": "Clase magistral generada correctamente."}
    except Exception as e:
        print(f"Error al generar clase magistral: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para borrar todos los datos de apuntes, chunks y vectorstores
@router.post("/borrar_apuntes_todos")
def borrar_apuntes_todos():
    """
    Borra todos los datos de apuntes, chunks y vectorstores.
    """
    limpiar_apuntes()
    return {"mensaje": "¡Todos los datos de apuntes, chunks y vectorstores han sido eliminados!"}