import typer
import shutil
from datetime import datetime
from pathlib import Path
from src.apuntes.scripts.rag_local import responder_con_groq, obtener_contexto
from src.apuntes.scripts.analizar_apuntes import analizar
from src.apuntes.scripts.crear_vectorstore import crear_vectorstore
from src.apuntes.scripts.actualizar_materias import cargar_base, guardar_base

app = typer.Typer(help="Tutor IA - CLI para estudiantes", no_args_is_help=True)
responder_app = typer.Typer(help="Subcomandos relacionados con respuestas")
procesar_app = typer.Typer(help="Subcomandos para procesar nuevos apuntes")
apuntes_app = typer.Typer(help="Comandos para subir apuntes nuevos")

@app.callback()
def main():
    """
    Tutor IA: un asistente educativo con capacidades de búsqueda y generación de respuestas.
    """
    pass

@responder_app.command("pregunta")
def responder_pregunta(
    materia: str = typer.Option(..., help="Nombre de la materia (ej: Historia)"),
    tema: str = typer.Option(..., help="Tema del que se hablará (ej: Rev Francesa)"),
    pregunta: str = typer.Option(..., help="Pregunta a responder (ej: ¿Qué causó la Revolución?)"),
):
    """
    Genera una respuesta usando RAG y el modelo de Groq.
    """
    contexto, advertencia = obtener_contexto(materia, tema, pregunta)

    if advertencia:
        typer.echo(advertencia)
        raise typer.Exit()

    typer.echo("⏳ Generando respuesta...\n")
    respuesta = responder_con_groq(materia, pregunta, contexto)
    typer.echo("🤖 Respuesta generada:\n")
    typer.echo(respuesta)

@responder_app.command("explicar_como_nino")
def explicar_como_nino(
    materia: str = typer.Option(..., help="Nombre de la materia (ej: Historia)"),
    tema: str = typer.Option(..., help="Tema del que se quiere una explicación"),
):
    """
    Explica el tema como si tuvieras 12 años.
    """
    pregunta_sintetica = f"Explícame el tema '{tema}' de la materia '{materia}' como si tuviera 12 años"
    contexto, advertencia = obtener_contexto(materia, tema, pregunta_sintetica)

    if advertencia:
        typer.echo(advertencia)
        raise typer.Exit()

    prompt = (
        f"Explica el siguiente tema de manera clara y sencilla, evitando tecnicismos innecesarios. "
        f"No uses un tono infantil ni exageradamente académico. Imagina que estás escribiendo para alguien "
        f"que no sabe mucho del tema, pero quiere entenderlo bien.\n\n"
        f"Organiza la explicación con buena estructura, frases directas y ejemplos cuando sean útiles. "
        f"No introduzcas saludos ni metáforas innecesarias. Limita la respuesta a un máximo de 200 palabras.\n\n"
        f"Tema: {tema} ({materia})\n\n"
        f"Contexto disponible:\n{contexto}\n\n"
        f"Ahora, genera una explicación clara, precisa y útil para cualquier lector interesado. "
        f"Recuerda: no más de 200 palabras."
    )

    typer.echo("🧒 Generando explicación simplificada...\n")
    respuesta = responder_con_groq(materia, pregunta_sintetica, prompt)
    typer.echo("📘 Explicación:\n")
    typer.echo(respuesta)

@procesar_app.command("nuevo")
def procesar_nuevo_apunte():
    """
    Ejecuta el flujo completo: analizar PDF, trocear texto y generar vectorstore.
    """
    typer.echo("📄 Paso 1: Analizando y troceando el apunte...")
    analizar()
    typer.echo("📦 Paso 2: Generando vectorstore...")
    crear_vectorstore()
    typer.echo("✅ Apunte procesado correctamente.")

@apuntes_app.command("subir")
def subir_apunte_cli(
    materia: str = typer.Option(..., help="Nombre de la materia"),
    tema: str = typer.Option(..., help="Nombre del tema"),
    archivo: str = typer.Option(..., help="Ruta del archivo PDF")
):
    base = cargar_base()

    # Crear la materia si no existe
    if materia not in base:
        base[materia] = {}

    # Crear el tema si no existe
    if tema not in base[materia]:
        base[materia][tema] = {"versiones": []}

    archivo_origen = Path(archivo)
    if not archivo_origen.exists():
        posible = Path("uploads") / archivo
        if posible.exists():
            archivo_origen = posible
        else:
            typer.echo(f"❌ El archivo '{archivo}' no existe ni en la ruta dada ni en 'uploads/'.")
            raise typer.Exit()

    fecha = datetime.today().strftime("%Y-%m-%d")
    nombre_base = archivo_origen.stem
    nuevo_nombre = f"{nombre_base}_v{len(base[materia][tema]['versiones']) + 1}.pdf"

    destino = Path("data/pdf") / nuevo_nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(archivo_origen, destino)

    base[materia][tema]["versiones"].append({
        "origen": archivo_origen.name,
        "archivo": nuevo_nombre,
        "fecha": fecha
    })

    guardar_base(base)
    typer.echo(f"✅ Apunte '{archivo_origen.name}' añadido correctamente a {materia} / {tema}.")

    # Paso 2: Procesar automáticamente el apunte
    typer.echo("📄 Analizando y troceando el apunte...")
    analizar(materia=materia, tema=tema)

    typer.echo("📦 Generando vectorstore...")
    crear_vectorstore(materia=materia, tema=tema)

    typer.echo("✅ Apunte procesado completamente.")


app.add_typer(responder_app, name="responder")
app.add_typer(procesar_app, name="procesar")
app.add_typer(apuntes_app, name="apuntes")

if __name__ == "__main__":
    app()