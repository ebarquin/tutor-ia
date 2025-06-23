import os
import json
from datetime import datetime
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR.parent.parent / "uploads"
DB_PATH = BASE_DIR / "db" / "materias.json"

def cargar_base():
    if DB_PATH.exists():
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {}

def guardar_base(base):
    with open(DB_PATH, "w") as f:
        json.dump(base, f, indent=4)

def listar_archivos_uploads():
    archivos = list(UPLOADS_DIR.glob("*.*"))
    if not archivos:
        print("❌ No hay archivos en la carpeta 'uploads/'. Añade al menos uno.")
        return None
    print("\nArchivos disponibles en 'uploads/':")
    for idx, archivo in enumerate(archivos):
        print(f"  [{idx}] {archivo.name}")
    seleccion = input("Selecciona el número del archivo que quieres subir: ")
    if not seleccion.isdigit() or int(seleccion) >= len(archivos):
        print("❌ Selección no válida.")
        return None
    return archivos[int(seleccion)]

def subir_apunte():
    base = cargar_base()

    archivo_seleccionado = listar_archivos_uploads()
    if archivo_seleccionado is None:
        return

    materia = input("Introduce el nombre de la materia: ").strip()
    tema = input("Introduce el nombre del tema: ").strip()

    nombre_archivo = archivo_seleccionado.name
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    version = f"v{len(base.get(materia, {}).get(tema, {}).get('versiones', [])) + 1}"
    nombre_destino = f"{Path(nombre_archivo).stem}_{version}{Path(nombre_archivo).suffix}"

    destino = DATA_DIR / materia / tema
    destino.mkdir(parents=True, exist_ok=True)
    shutil.copy2(archivo_seleccionado, destino / nombre_destino)

    # Actualizamos la base de datos
    if materia not in base:
        base[materia] = {}
    if tema not in base[materia]:
        base[materia][tema] = {"versiones": []}

    base[materia][tema]["versiones"].append({
        "archivo": nombre_destino,
        "fecha": fecha_actual,
        "origen": nombre_archivo
    })

    guardar_base(base)
    print(f"✅ Apuntes subidos correctamente como {nombre_destino}")

if __name__ == "__main__":
    subir_apunte()
