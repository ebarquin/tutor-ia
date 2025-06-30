from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BASE_DIR = Path(__file__).resolve().parents[4]  # Sube hasta la raíz del repo
VECTORSTORE_DIR = BASE_DIR / "src" / "apuntes" / "rag" / "vectorstores"

import os
llm = ChatOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama3-70b-8192",
    temperature=0.2
)

def cargar_vectorstore(materia: str, tema: str):
    """
    Carga el vectorstore de una materia y tema concretos.
    """
    ruta = VECTORSTORE_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}"
    print("[DEBUG] Ruta absoluta buscada:", ruta.resolve())
    if not ruta.exists():
        print("NO SE ENCONTRÓ EL VECTORSTORE.")
        return None
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    store = FAISS.load_local(str(ruta), embeddings, allow_dangerous_deserialization=True)
    return store

def obtener_todo_contexto_vectorstore(materia: str, tema: str, max_chunks: int = 40) -> str:
    """
    Devuelve un contexto largo concatenando TODOS los fragmentos/chunks de los apuntes para un tema.
    Limita el número de chunks para no pasarse de tokens.
    """
    store = cargar_vectorstore(materia, tema)
    if not store:
        return ""
    docs = store.similarity_search("", k=max_chunks)
    contexto = "\n\n".join(doc.page_content.strip() for doc in docs)
    return contexto

def analizar_lagunas_en_contexto_tool(materia: str, tema: str, modelo_llm) -> str:
    """
    Usa el LLM para analizar TODOS los apuntes del vectorstore y detectar carencias, omisiones, incoherencias o posibles lagunas relevantes.
    """
    contexto = obtener_todo_contexto_vectorstore(materia, tema)
    if not contexto:
        return "No se encontró información suficiente en los apuntes."

    prompt = (
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
    respuesta = modelo_llm.invoke(prompt)
    return respuesta

if __name__ == "__main__":
    materia = "historia"
    tema = "la_revolucion_francesa"
    # Asegúrate de que estos nombres existen tal cual en tu vectorstore
    respuesta = analizar_lagunas_en_contexto_tool(materia, tema, modelo_llm=llm)
    print(respuesta)