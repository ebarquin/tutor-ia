# src/api/main.py

from fastapi import FastAPI
from src.api.routes import cli_routes

app = FastAPI()
app.include_router(cli_routes.router)

@app.get("/")
def home():
    return {"mensaje": "¡Tu API está funcionando correctamente en Render!"}