from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.apuntes.scripts.agents.agent_tools import cargar_vectorstore, VECTORSTORE_DIR
import shutil

materia = "historia"
tema = "primera_guerra_mundial"
output_dir = VECTORSTORE_DIR / f"{materia}__{tema}_filtrado"

# Paso 1: cargar original
store = cargar_vectorstore(materia, tema)
docs = store.similarity_search("", k=1000)

# Paso 2: filtrar los que no fueron añadidos por LLM
docs_filtrados = [doc for doc in docs if doc.metadata.get("fuente") != "expansion_llm"]

# Paso 3: recrear vectorstore desde 0
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
nuevo_store = FAISS.from_documents(docs_filtrados, embedding)

# Paso 4: guardar el nuevo
nuevo_store.save_local(str(output_dir))

# Paso 5 (opcional): reemplazar el original
shutil.rmtree(VECTORSTORE_DIR / f"{materia}__{tema}")
shutil.move(str(output_dir), str(VECTORSTORE_DIR / f"{materia}__{tema}"))


# from src.apuntes.scripts.agents.agent_tools import cargar_vectorstore

# materia = "historia"
# tema = "primera_guerra_mundial"

# store = cargar_vectorstore(materia, tema)
# if not store:
#     print("❌ No se pudo cargar el vectorstore.")
#     exit()

# docs = store.similarity_search("", k=1000)

# chunks_llm = [
#     doc for doc in docs
#     if doc.metadata.get("fuente") == "expansion_llm"
# ]

# print(f"🧠 Total de chunks generados por el LLM: {len(chunks_llm)}")