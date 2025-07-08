from pydantic import BaseModel
from typing import List, Literal

class MensajeChat(BaseModel):
    role: Literal["user", "tutor"]
    content: str

class ChatExplicaSimpleRequest(BaseModel):
    materia: str
    tema: str
    historial: List[MensajeChat]

class ChatExplicaSimpleResponse(BaseModel):
    respuesta: str
    historial: List[MensajeChat]