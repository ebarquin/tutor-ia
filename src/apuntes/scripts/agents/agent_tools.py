from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from pathlib import Path
import os
import json
import re

# Constantes globales
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BASE_DIR = Path(__file__).resolve().parents[4]  # Ajusta si cambia la estructura del repo
VECTORSTORE_DIR = BASE_DIR / "src" / "apuntes" / "rag" / "vectorstores"

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
        return "No se pudo enriquecer los apuntes por falta de información."

    puntos = resultado.get("ausencias", []) + resultado.get("subtemas_recomendados", [])
    nuevos_chunks = []

    for punto in puntos:
        expansion = generar_chunk_expansion_tool(materia, tema, punto, contexto, modelo_llm)
        if expansion and "ya está cubierto" not in expansion.lower():
            nuevos_chunks.append({"punto": punto, "texto": expansion})

    if not nuevos_chunks:
        return "No se generaron nuevos chunks."

    insertar_chunks_en_vectorstore(nuevos_chunks, materia, tema)
    return f"{len(nuevos_chunks)} nuevos chunks añadidos correctamente."
