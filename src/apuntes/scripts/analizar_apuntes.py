import os
import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber

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

def trocear_texto(texto, materia, tema, fuente):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = splitter.split_text(texto)
    resultado = []
    for i, chunk in enumerate(chunks):
        resultado.append({
            "materia": materia,
            "tema": tema,
            "chunk_id": f"{materia.lower().replace(' ', '_')}_{tema.lower().replace(' ', '_')}_{i+1}",
            "texto": chunk,
            "metadatos": {
                "fuente": fuente,
                "posición": i+1
            }
        })
    return resultado

def analizar(materia: str = None, tema: str = None):
    base = cargar_base()
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
    ultima = versiones[-1]["archivo"]
    archivo_path = Path("data/pdf") / ultima

    if not archivo_path.exists():
        print("❌ Archivo no encontrado:", archivo_path)
        return

    print(f"🔍 Analizando: {archivo_path.name}")
    texto = extraer_texto_pdf(archivo_path)
    chunks = trocear_texto(texto, materia, tema, ultima)

    output_file = CHUNKS_DIR / f"{materia.lower().replace(' ', '_')}__{tema.lower().replace(' ', '_')}.json"
    with open(output_file, "w") as f:
        json.dump(chunks, f, indent=4)

    print(f"✅ {len(chunks)} fragmentos generados y guardados en {output_file}")

if __name__ == "__main__":
    analizar()
