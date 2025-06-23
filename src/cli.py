import typer
from src.services.tutor import (
    responder_pregunta_servicio,
    explicar_como_nino_servicio,
    procesar_apunte_completo
)

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
    materia: str = typer.Option(...),
    tema: str = typer.Option(...),
    pregunta: str = typer.Option(...),
):
    """Genera una respuesta usando RAG y el modelo de Groq."""
    try:
        respuesta = responder_pregunta_servicio(materia, tema, pregunta)
        typer.echo("🤖 Respuesta generada:\n")
        typer.echo(respuesta)
    except ValueError as e:
        typer.echo(str(e))


@responder_app.command("explicar_como_nino")
def explicar_para_ninos(
    materia: str = typer.Option(...),
    tema: str = typer.Option(...),
):
    """Explica el tema como si tuvieras 12 años."""
    try:
        respuesta = explicar_como_nino_servicio(materia, tema)
        typer.echo("📘 Explicación:\n")
        typer.echo(respuesta)
    except ValueError as e:
        typer.echo(str(e))

@procesar_app.command("nuevo")
def procesar_nuevo_apunte(
    materia: str = typer.Option(...),
    tema: str = typer.Option(...),
    archivo: str = typer.Option(...),
):
    """Ejecuta el flujo completo: analiza PDF, trocea texto y genera vectorstore."""
    try:
        mensaje = procesar_apunte_completo(materia, tema, archivo)
        typer.echo(mensaje)
    except Exception as e:
        typer.echo(f"❌ Error: {str(e)}")

app.add_typer(responder_app, name="responder")
app.add_typer(procesar_app, name="procesar")
app.add_typer(apuntes_app, name="apuntes")

if __name__ == "__main__":
    app()