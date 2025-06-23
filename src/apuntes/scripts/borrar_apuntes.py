import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "db" / "materias.json"

def borrar_apunte():
    if not DB_PATH.exists():
        print("❌ No se encontró el archivo 'materias.json'")
        return

    with open(DB_PATH, "r") as f:
        base = json.load(f)

    if not base:
        print("📂 No hay apuntes registrados.")
        return

    print("\nMaterias registradas:")
    materias = list(base.keys())
    for i, m in enumerate(materias):
        print(f"  [{i}] {m}")

    idx_m = input("Selecciona el número de la materia que quieres limpiar: ")
    if not idx_m.isdigit() or int(idx_m) >= len(materias):
        print("❌ Selección no válida.")
        return

    materia = materias[int(idx_m)]
    temas = list(base[materia].keys())
    print(f"\nTemas en '{materia}':")
    for i, t in enumerate(temas):
        print(f"  [{i}] {t}")

    idx_t = input("Selecciona el número del tema que quieres borrar: ")
    if not idx_t.isdigit() or int(idx_t) >= len(temas):
        print("❌ Selección no válida.")
        return

    tema = temas[int(idx_t)]

    # Borrar carpeta física
    carpeta = DATA_DIR / materia / tema
    if carpeta.exists():
        shutil.rmtree(carpeta)
        print(f"🧹 Carpeta '{carpeta}' eliminada.")

    # Borrar del JSON
    del base[materia][tema]
    if not base[materia]:
        del base[materia]

    with open(DB_PATH, "w") as f:
        json.dump(base, f, indent=4)

    print(f"✅ Tema '{tema}' de la materia '{materia}' ha sido eliminado completamente.")

if __name__ == "__main__":
    borrar_apunte()
