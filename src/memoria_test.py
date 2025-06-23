import os
import psutil
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

FAISS_DIR = "src/apuntes/rag/vectorstores/economía__economía_política"

def medir_memoria():
    proceso = psutil.Process(os.getpid())
    mem_bytes = proceso.memory_info().rss
    mem_megas = mem_bytes / (1024 ** 2)
    print(f"🔍 Memoria usada: {mem_megas:.2f} MB")

print("✅ Inicio")
medir_memoria()

print("\n📦 Cargando vectorstore...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(FAISS_DIR, embeddings, allow_dangerous_deserialization=True)
medir_memoria()

print("\n🔍 Haciendo consulta...")
docs = vectorstore.similarity_search("¿Qué es la política fiscal?", k=3)
for doc in docs:
    print("-", doc.page_content[:100], "...")

medir_memoria()