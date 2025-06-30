from dotenv import load_dotenv
load_dotenv()
from src.apuntes.scripts.agents.agent_tools import cargar_vectorstore, obtener_todo_contexto_vectorstore
from langchain_openai import ChatOpenAI
import os

materia = "historia"
tema = "primera_guerra_mundial"

# Debug: carga y muestra info del store
store = cargar_vectorstore(materia, tema)
if not store:
    print("NO SE ENCONTRÓ EL VECTORSTORE.")
    exit()
try:
    print("[DEBUG] store.docstore:", getattr(store, 'docstore', 'NO docstore'))
    print("[DEBUG] Cantidad de documentos en store:", len(store.docstore._dict))
except Exception as e:
    print("DEBUG ERROR:", e)

# Prueba similarity_search con query universal
docs = store.similarity_search("", k=40)
print(f"[DEBUG] Chunks recuperados con '': {len(docs)}")
for i, doc in enumerate(docs, 1):
    print(f"--- Chunk {i} ---\n{doc.page_content}\n")

# Prueba con otra query aún más genérica
docs = store.similarity_search("el", k=40)
print(f"[DEBUG] Chunks recuperados con 'el': {len(docs)}")
for i, doc in enumerate(docs, 1):
    print(f"--- Chunk {i} ---\n{doc.page_content}\n")