# src/api/main.py

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"mensaje": "¡Tu API está funcionando correctamente en Render!"}