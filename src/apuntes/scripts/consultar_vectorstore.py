import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent
FAISS_DIR = BASE_DIR / "rag" / "vectorstores"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def cargar_vectorstore(materia, tema):
    ruta = FAISS_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}"
    if not ruta.exists():
        print(f"❌ No se encontró el vectorstore en: {ruta}")
        return None

    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    store = FAISS.load_local(str(ruta), embeddings, allow_dangerous_deserialization=True)
    return store

def consultar():
    materia = input("Materia (ej: Historia): ").strip()
    tema = input("Tema (ej: Rev Francesa): ").strip()

    store = cargar_vectorstore(materia, tema)
    if not store:
        return

    while True:
        query = input("\n🧠 Pregunta ('exit' para salir): ").strip()
        if query.lower() == "exit":
            break

        docs = store.similarity_search(query, k=3)
        print("\n🔎 Resultados más relevantes:")
        for i, doc in enumerate(docs, 1):
            print(f"--- Fragmento {i} ---")
            print(doc.page_content.strip())
            print()

if __name__ == "__main__":
    consultar()
