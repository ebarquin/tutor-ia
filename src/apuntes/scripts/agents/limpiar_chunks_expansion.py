from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.apuntes.scripts.agents.agent_tools import cargar_vectorstore, VECTORSTORE_DIR
import shutil
import os
from pathlib import Path
from src.config import OPENAI_API_KEY


def limpiar_expansion_en_todos():
    vectorstore_dir = VECTORSTORE_DIR
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    total_chunks_eliminados = 0

    # Recorre todas las carpetas de vectorstore (una por materia__tema)
    for folder in os.listdir(vectorstore_dir):
        folder_path = vectorstore_dir / folder
        if not folder_path.is_dir():
            continue

        # Parsear materia y tema
        try:
            materia, tema = folder.split("__")
        except ValueError:
            print(f"Saltando carpeta {folder} (no cumple formato esperado)")
            continue

        print(f"Limpiando vectorstore para {materia=} {tema=}")

        try:
            # Cargar vectorstore
            store = cargar_vectorstore(materia, tema)
            docs = store.similarity_search("", k=1000)

            # Filtrar los que no fueron añadidos por LLM
            docs_filtrados = [doc for doc in docs if doc.metadata.get("fuente") != "expansion_llm"]
            chunks_eliminados = len(docs) - len(docs_filtrados)
            total_chunks_eliminados += chunks_eliminados

            if chunks_eliminados == 0:
                print(f"  No había chunks de expansión para borrar.")
                continue

            # Recrear vectorstore desde 0 y guardar temporalmente
            output_dir = vectorstore_dir / f"{materia}__{tema}_filtrado"
            nuevo_store = FAISS.from_documents(docs_filtrados, embedding)
            nuevo_store.save_local(str(output_dir))

            # Reemplazar original
            shutil.rmtree(folder_path)
            shutil.move(str(output_dir), str(folder_path))
            print(f"  Eliminados {chunks_eliminados} chunks de expansión en {materia} - {tema}.")
        except Exception as e:
            print(f"  [ERROR] No se pudo procesar {materia} - {tema}: {e}")
            continue

    print(f"Total de chunks de expansión eliminados: {total_chunks_eliminados}")

if __name__ == "__main__":
    limpiar_expansion_en_todos()

from src.apuntes.scripts.agents.agent_tools import generar_clase_magistral_en_bloques
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from src.apuntes.scripts.agents.agent_tools import generar_clase_magistral_en_bloques, tts_func
from langchain_openai import ChatOpenAI
import os

modelo_llm = ChatOpenAI(
    api_key= OPENAI_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    model="llama3-70b-8192",
    temperature=0.2
)

resultado = generar_clase_magistral_en_bloques(
    "historia",
    "segunda_guerra_mundial",
    modelo_llm,
    tts_func=tts_func,
    max_titulos_bloque=12  # Puedes ajustar este valor
)

print("\n---- TEXTO DE LA CLASE ----\n")
print(resultado["clase_magistral_texto"])
print("\nRuta del archivo de audio generado:", resultado["audio_url"])