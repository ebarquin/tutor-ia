# src/apuntes/scripts/agent_test.py

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from agent_tools import consulta_apuntes_tool

llm = ChatOpenAI(
    api_key="tu_groq_api_key",
    base_url="https://api.groq.com/openai/v1",
    model="llama3-70b-8192",
    temperature=0.2
)

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
            "Debes proporcionar una pregunta relacionada con el tema de estudio."
        ),
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

print(agent.invoke("¿Qué es el feudalismo?"))