from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from src.apuntes.scripts.agents.agent_tools import (
    consulta_apuntes_tool,
    analizar_lagunas_en_contexto_tool,
    generar_chunk_expansion_tool,
    insertar_chunks_en_vectorstore_tool,
    enriquecer_apuntes_tool
)
import os

# Inicializar LLM
llm = ChatOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama3-70b-8192",
    temperature=0.2
)

# Definir herramientas del agente
tools = [
    Tool(
        name="ConsultarApuntes",
        func=lambda pregunta: consulta_apuntes_tool(
            materia="historia",
            tema="la_edad_media",
            pregunta=pregunta
        ),
        description=(
            "Usa esta herramienta para buscar información relevante en los apuntes del estudiante. "
        ),
    ),
    Tool(
        name="AnalizarLagunasEnContexto",
        func=lambda input: analizar_lagunas_en_contexto_tool(
            materia=input["materia"],
            tema=input["tema"],
            modelo_llm=llm
        ),
        description="Analiza si los apuntes de una materia y tema tienen carencias, lagunas o incoherencias relevantes."
    ),
    Tool(
        name="InsertarChunksEnApuntes",
        func=lambda input: insertar_chunks_en_vectorstore_tool(
            nuevos_chunks=input["nuevos_chunks"],
            materia=input["materia"],
            tema=input["tema"]
        ),
        description=(
            "Usa esta herramienta para insertar nuevos fragmentos generados por el LLM en los apuntes de una materia y tema concretos. "
            "Debes proporcionar una lista de nuevos_chunks (cada uno con 'punto' y 'texto'), la materia y el tema."
        ),
    ),
    Tool(
        name="EnriquecerApuntesAutomaticamente",
        func=lambda input: enriquecer_apuntes_tool(
            materia=input["materia"],
            tema=input["tema"],
            modelo_llm=llm
        ),
        description=(
            "Analiza los apuntes, genera automáticamente los fragmentos que faltan y los añade al vectorstore. "
            "Solo debes indicar la materia y el tema."
        ),
    )
]

# Inicializar agente
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Ejemplo de uso directo
if __name__ == "__main__":
    print(agent.invoke("¿Qué es el feudalismo?"))