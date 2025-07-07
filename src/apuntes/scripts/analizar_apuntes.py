import os
import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
from transformers import pipeline
from openai import OpenAI
from src.config import GROQ_API_KEY

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "db" / "materias.json"
CHUNKS_DIR = BASE_DIR / "rag" / "chunks"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

def cargar_base():
    if DB_PATH.exists():
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {}

def extraer_texto_pdf(archivo_path):
    texto = ""
    with pdfplumber.open(archivo_path) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() + "\n"
    return texto

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def generar_titulo(chunk_text):
    prompt = (
        "Resume el siguiente texto en un título breve, claro y representativo del contenido. "
        "Debe ser completo, sin cortar palabras ni poner puntos suspensivos. "
        "Ideal para un apunte académico (máximo 80 caracteres):\n\n"
        f"{chunk_text}\n\nTítulo:"
    )
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=32,
        temperature=0.5
    )
    raw = response.choices[0].message.content.strip()
    # Normaliza salida
    if "Título:" in raw:
        titulo = raw.split("Título:")[-1].strip()
    else:
        titulo = raw.strip()
    return titulo

def trocear_texto(texto, materia, tema, fuente):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = splitter.split_text(texto)
    resultado = []
    for i, chunk in enumerate(chunks):
        titulo_generado = generar_titulo(chunk)
        resultado.append({
            "materia": materia,
            "tema": tema,
            "chunk_id": f"{materia.lower().replace(' ', '_')}_{tema.lower().replace(' ', '_')}_{i+1}",
            "texto": chunk,
            "titulo": titulo_generado,
            "metadatos": {
                "fuente": fuente,
                "posición": i+1
            }
        })
    return resultado
def analizar(materia: str = None, tema: str = None):
    base = cargar_base()
    print("DEBUG: Base cargada:", base)
    if not base:
        print("❌ No hay datos en 'materias.json'")
        return

    if materia is None or tema is None:
        print("\nMaterias disponibles:")
        materias = list(base.keys())
        for i, mat in enumerate(materias):
            print(f"  [{i}] {mat}")
        idx_m = int(input("Selecciona la materia: "))
        materia = materias[idx_m]

        temas = list(base[materia].keys())
        print(f"\nTemas en '{materia}':")
        for i, tem in enumerate(temas):
            print(f"  [{i}] {tem}")
        idx_t = int(input("Selecciona el tema: "))
        tema = temas[idx_t]

    versiones = base[materia][tema]["versiones"]
    print("DEBUG: Versiones encontradas para tema:", versiones)
    if not versiones:
        print("❌ No hay versiones de PDF para este tema.")
        return

    ultima = versiones[-1]["archivo"]
    archivo_path = Path("data/pdf") / ultima
    print("DEBUG: Archivo PDF a procesar:", archivo_path)

    if not archivo_path.exists():
        print("❌ Archivo no encontrado:", archivo_path)
        return

    print(f"🔍 Analizando: {archivo_path.name}")
    texto = extraer_texto_pdf(archivo_path)
    print("DEBUG: Texto extraído, longitud:", len(texto))
    chunks = trocear_texto(texto, materia, tema, ultima)
    print("DEBUG: Número de chunks generados:", len(chunks))

    output_file = CHUNKS_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}.json"
    with open(output_file, "w") as f:
        json.dump(chunks, f, indent=4)
    print("DEBUG: Archivo JSON guardado en:", output_file)

    print(f"✅ {len(chunks)} fragmentos generados y guardados en {output_file}")

if __name__ == "__main__":
    analizar()
