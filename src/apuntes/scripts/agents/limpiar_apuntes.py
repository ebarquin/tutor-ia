import shutil
from pathlib import Path
import os

RUTAS_A_LIMPIAR = [
    "src/apuntes/rag/vectorstores",
    "src/apuntes/rag/chunks",
    "data/pdf",
    "uploads"
]
ARCHIVOS_A_BORRAR = [
    "src/apuntes/db/materias.json"
]

def limpiar_directorio(ruta):
    p = Path(ruta)
    if p.exists():
        for child in p.iterdir():
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)

def limpiar_apuntes():
    for ruta in RUTAS_A_LIMPIAR:
        limpiar_directorio(ruta)
        print(f"🧹 Directorio '{ruta}' limpiado.")
    for archivo in ARCHIVOS_A_BORRAR:
        p = Path(archivo)
        if p.exists():
            p.unlink()
            print(f"🗑️ Archivo '{archivo}' borrado.")
        else:
            print(f"⚠️ Archivo '{archivo}' no existe, no hay que borrar nada.")

if __name__ == "__main__":
    limpiar_apuntes()
    print("✅ Proyecto limpio como una patena. ¡Listo para pruebas!")