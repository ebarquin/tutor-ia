import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "materias.json"

def ver_apuntes():
    if not DB_PATH.exists():
        print("❌ No se encontró el archivo 'materias.json'")
        return

    with open(DB_PATH, "r") as f:
        base = json.load(f)

    if not base:
        print("📂 No hay apuntes registrados.")
        return

    print("\n📘 Apuntes registrados:")
    for materia, temas in base.items():
        print(f"  📚 Materia: {materia}")
        for tema, datos in temas.items():
            print(f"    📄 Tema: {tema}")
            for i, version in enumerate(datos.get("versiones", []), 1):
                print(f"      V{i}: {version['archivo']} (subido el {version['fecha']})")
    print("")

if __name__ == "__main__":
    ver_apuntes()
