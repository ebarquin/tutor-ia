import shutil
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "db" / "materias.json"

def limpiar_todo():
    confirm = input("⚠️ ¿Estás seguro de que quieres borrar TODOS los apuntes y registros? (sí/no): ").strip().lower()
    if confirm != "sí":
        print("❌ Operación cancelada.")
        return

    # Borrar carpeta de datos
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
        print("🧹 Carpeta 'data/' eliminada.")

    # Vaciar archivo JSON
    with open(DB_PATH, "w") as f:
        json.dump({}, f, indent=4)
    print("🧾 Archivo 'materias.json' limpiado.")

    print("✅ El entorno ha sido restaurado a estado limpio.")

if __name__ == "__main__":
    limpiar_todo()
