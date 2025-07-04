import os
import json
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import Optional, List, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_DIR = BASE_DIR / "rag" / "chunks"
FAISS_DIR = BASE_DIR / "rag" / "vectorstores"
FAISS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def cargar_chunks(materia, tema):
    archivo = CHUNKS_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}.json"
    if not archivo.exists():
        print(f"❌ No se encontró el archivo: {archivo}")
        return []

    with open(archivo, "r") as f:
        datos = json.load(f)

    documentos = []
    for chunk in datos:
        metadatos = chunk.get("metadatos", {}).copy()
        metadatos.update({
            "materia": chunk.get("materia"),
            "tema": chunk.get("tema"),
            "chunk_id": chunk.get("chunk_id"),
            # <<< Añade esto para asegurar título aunque esté suelto >>>
            "titulo": chunk.get("titulo") or metadatos.get("titulo"),
        })
        documentos.append(Document(page_content=chunk["texto"], metadata=metadatos))
    return documentos

def crear_vectorstore(materia: Optional[str] = None, tema: Optional[str] = None):
    if materia is None:
        materia = input("Materia (ej: Historia): ").strip()
    if tema is None:
        tema = input("Tema (ej: Rev Francesa): ").strip()

    documentos = cargar_chunks(materia, tema)
    if not documentos:
        print("❌ No se encontraron documentos para crear el vectorstore.")
        return

    print(f"🔍 Generando embeddings con '{MODEL_NAME}'...")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

    print(f"📦 Creando FAISS vectorstore con {len(documentos)} documentos...")
    vectorstore = FAISS.from_documents(documentos, embeddings)

    ruta_guardado = FAISS_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}"
    vectorstore.save_local(str(ruta_guardado))
    print(f"✅ Vectorstore guardado en: {ruta_guardado}")

if __name__ == "__main__":
    crear_vectorstore()
