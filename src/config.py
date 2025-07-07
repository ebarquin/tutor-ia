import os
from dotenv import load_dotenv

# Carga las variables desde un archivo .env si existe
load_dotenv()

# Variables comunes
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# API keys o secretos
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Rutas del sistema
BASE_VECTORSTORE_PATH = os.getenv("BASE_VECTORSTORE_PATH", "./data/vectorstores")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")