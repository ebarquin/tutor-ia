from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, tool, AgentType
import os
from dotenv import load_dotenv

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

llm = ChatOpenAI(
    api_key= groq_key,
    base_url="https://api.groq.com/openai/v1",
    model="llama3-70b-8192",
    temperature=0.2
)

@tool
def dummy_tool(input: str) -> str:
    """Una tool de ejemplo que solo repite el input."""
    return f"ECO: {input}"

tools = [dummy_tool]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

print(agent.invoke("¿Cuál es la capital de Francia?"))