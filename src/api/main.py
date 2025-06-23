from fastapi import FastAPI
from src.api.routes import cli_routes  # asegúrate del path correcto

app = FastAPI()
app.include_router(cli_routes.router)