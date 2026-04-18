from fastapi import APIRouter
from pydantic import BaseModel
from core.services.chatbot import responder_chat

#Creación del router para las rutas del chatbot
router = APIRouter()

class Mensaje(BaseModel):
    mensaje: str

# Endpoint para recibir mensajes del chatbot y responder
@router.post("/chat")
def chat_api(data: Mensaje):
    respuesta = responder_chat(data.mensaje)
    return {"respuesta": respuesta}