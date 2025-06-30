from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = Path(__file__).resolve().parent.parent / "rag" / "vectorstores"

def cargar_vectorstore(materia: str, tema: str):
    """
    Carga el vectorstore de una materia y tema concretos.
    """
    ruta = VECTORSTORE_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}"
    if not ruta.exists():
        return None
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    store = FAISS.load_local(str(ruta), embeddings, allow_dangerous_deserialization=True)
    return store

def obtener_contexto_vectorstore(materia: str, tema: str, pregunta: str, k: int = 4) -> str:
    """
    Devuelve un contexto relevante de los apuntes para una pregunta dada.
    """
    store = cargar_vectorstore(materia, tema)
    if not store:
        return ""
    docs = store.similarity_search(pregunta, k=k)
    contexto = "\n\n".join(doc.page_content.strip() for doc in docs)
    return contexto

def consulta_apuntes_tool(materia: str, tema: str, pregunta: str) -> str:
    """
    Tool principal para consultar los apuntes de una materia y tema.
    """
    contexto = obtener_contexto_vectorstore(materia, tema, pregunta)
    if not contexto:
        return "No se encontró información relevante en los apuntes."
    return contexto

if __name__ == "__main__":
    materia = "historia"
    tema = "la_edad_media"
    pregunta = "¿Qué fue el feudalismo?"
    contexto = obtener_contexto_vectorstore(materia, tema, pregunta)
    print("Contexto encontrado:\n")
    print(contexto if contexto else "No se encontró información.")