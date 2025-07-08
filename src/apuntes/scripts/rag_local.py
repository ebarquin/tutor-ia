# src/apuntes/scripts/rag_local.py

import torch
import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from pathlib import Path
from src.config import GROQ_API_KEY, HUGGINGFACE_TOKEN


# Cargar variables de entorno
load_dotenv()
token = HUGGINGFACE_TOKEN
groq_key = GROQ_API_KEY

# Cliente de Groq
client = OpenAI(
    api_key=groq_key,
    base_url="https://api.groq.com/openai/v1"
)

# Configuración
BASE_DIR = Path(__file__).resolve().parent.parent
FAISS_DIR = BASE_DIR / "rag" / "vectorstores"

def es_pregunta_relevante(materia, tema, pregunta, umbral=0.7):
    store = cargar_vectorstore(materia, tema)
    if not store:
        print("No se pudo cargar el vectorstore para", materia, tema)
        return False
    docs_con_score = store.similarity_search_with_score(pregunta, k=3)
    if not docs_con_score:
        print("No se encontraron chunks similares.")
        return False
    for doc, score in docs_con_score:
        print(f"Score: {score:.3f} - Texto chunk: {doc.page_content[:100]}")
    # Usamos el score máximo porque refleja la mayor relevancia de algún chunk respecto a la pregunta
    score_max = max(score for doc, score in docs_con_score)
    print(f"Score máximo: {score_max}")
    return score_max > umbral

def cargar_vectorstore(materia, tema):
    """Carga el vectorstore para una materia y tema específico."""
    ruta = FAISS_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}"
    if not ruta.exists():
        print(f"❌ No se encontró el vectorstore en: {ruta}")
        return None
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(str(ruta), embeddings, allow_dangerous_deserialization=True)


def obtener_contexto(materia, tema, pregunta):
    """Devuelve contexto relevante basado en el vectorstore."""
    store = cargar_vectorstore(materia, tema)
    if not store:
        return None, "❌ No se encontró el vectorstore para esa materia y tema."

    docs_con_score = store.similarity_search_with_score(pregunta, k=3)

    print("\n📊 Resultados de similitud:")
    for doc, score in docs_con_score:
        print(f"Score: {score:.4f} | Contenido: {doc.page_content[:100]}...")

    docs_filtrados = [doc for doc, score in docs_con_score if score > 0.55]

    if not docs_filtrados:
        return None, "⚠️ La pregunta no parece estar relacionada con los apuntes disponibles."

    contexto = "\n---\n".join([doc.page_content for doc in docs_filtrados])
    return contexto, None


def responder_con_groq(materia, pregunta, contexto):
    """Usa Groq para generar una respuesta basada en el contexto."""
    if not contexto:
        return (
            "Lo siento, no tengo información suficiente en los apuntes para responder a esa pregunta."
        )

    prompt = (
        f"Eres un profesor experto en {materia}. "
        f"Responde a la pregunta solo si el contexto tiene información suficiente. "
        f"Si no puedes encontrar una respuesta clara en el texto, di educadamente que no puedes responder.\n\n"
        f"--- CONTEXTO ---\n{contexto}\n\n"
        f"--- PREGUNTA ---\n{pregunta}\n\n"
        f"--- RESPUESTA ---"
    )

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "Responde solo si tienes información suficiente en el contexto. No inventes ni divagues."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.2,
        top_p=0.9
    )

    return response.choices[0].message.content.strip()


# --- CLI para pruebas manuales ---
def main():
    materia = input("Materia (ej: Historia): ").strip()
    tema = input("Tema (ej: Rev Francesa): ").strip()
    pregunta = input("🧠 Pregunta: ").strip()

    contexto, advertencia = obtener_contexto(materia, tema, pregunta)
    if advertencia:
        print(f"\n{advertencia}")
        return

    print("\n⏳ Generando respuesta...")
    respuesta = responder_con_groq(materia, pregunta, contexto)
    print("\n🤖 Respuesta generada:")
    print(respuesta)


if __name__ == "__main__":
    main()