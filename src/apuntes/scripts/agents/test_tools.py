from dotenv import load_dotenv
load_dotenv()

import os
from langchain_openai import ChatOpenAI
from src.apuntes.scripts.agents.agent_tools import (
    cargar_vectorstore,
    obtener_todo_contexto_vectorstore,
    analizar_lagunas_en_contexto_tool,
    generar_chunk_expansion_tool,
    insertar_chunks_en_vectorstore_tool
)

materia = "historia"
tema = "primera_guerra_mundial"

# Inicializar LLM
llm = ChatOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama3-70b-8192",
    temperature=0.2
)

# --- Cargar y verificar vectorstore ---
store = cargar_vectorstore(materia, tema)
if not store:
    print("❌ NO SE ENCONTRÓ EL VECTORSTORE.")
    exit()

try:
    print("[DEBUG] Cantidad de documentos en store:", len(store.docstore._dict))
except Exception as e:
    print("DEBUG ERROR:", e)

# --- Paso 1: Análisis de lagunas ---
print("🧠 Ejecutando análisis de lagunas...\n")
resultado = analizar_lagunas_en_contexto_tool(materia, tema, llm)

if not resultado or "error" in resultado:
    print("⚠️ No se pudo realizar el análisis de lagunas.")
    exit()

print("✅ Resultado del análisis:\n")
print(resultado)

# --- Paso 2: Generación automática de chunks ---
print("\n🧩 Generando nuevos chunks de expansión...\n")
contexto = obtener_todo_contexto_vectorstore(materia, tema)
puntos = resultado.get("ausencias", []) + resultado.get("subtemas_recomendados", [])
nuevos_chunks = []

for punto in puntos:
    expansion = generar_chunk_expansion_tool(materia, tema, punto, contexto, llm)
    if expansion and "ya está cubierto" not in expansion.lower():
        print(f"✔️ Chunk generado para: {punto}\n{expansion}\n")
        nuevos_chunks.append({"punto": punto, "texto": expansion})
    else:
        print(f"🔁 El punto '{punto}' ya estaba cubierto o fue descartado.\n")

# --- Paso 3: Inserción en el vectorstore ---
if nuevos_chunks:
    print(f"💾 Insertando {len(nuevos_chunks)} nuevos chunks en el vectorstore...")
    resultado_insercion = insertar_chunks_en_vectorstore_tool(nuevos_chunks, materia, tema)
    print(f"✅ Resultado de la inserción: {resultado_insercion}")
else:
    print("ℹ️ No se generaron nuevos chunks, no hay nada que insertar.")