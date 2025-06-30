from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from apuntes.scripts.agents.agent_tools import consulta_apuntes_tool, analizar_lagunas_en_contexto_tool

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
    ),

    Tool(
    name="analizar_lagunas_en_contexto",
    func=lambda input: analizar_lagunas_en_contexto_tool(
        contexto=input["contexto"], tema=input["tema"], modelo_llm=llm
    ),
    description="Analiza si los apuntes dados sobre un tema tienen carencias, lagunas o incoherencias relevantes."
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

print(agent.invoke("¿Qué es el feudalismo?"))