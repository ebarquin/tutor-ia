import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "materias.json"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def cargar_base():
    if DB_PATH.exists():
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {}

def guardar_base(base):
    with open(DB_PATH, "w") as f:
        json.dump(base, f, indent=4)

def añadir_materia(materia: str):
    base = cargar_base()
    if materia in base:
        print(f"⚠️ La materia '{materia}' ya existe.")
        return
    base[materia] = {}
    guardar_base(base)
    print(f"✅ Materia '{materia}' añadida correctamente.")