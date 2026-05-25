from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from infra.db.database import get_db
from core.schemas.chat import ChatRequest
from core.services.chatbot import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chatbot IA - Akaza"])

@router.post("/mensaje")
def hablar_con_akaza(request: ChatRequest, db: Session = Depends(get_db)):
  """Ingests dialogue messages from customers and interacts with Akaza AI chatbot."""
  chat_service = ChatService(db)

  try:
    respuesta = chat_service.procesar_mensaje(
      id_usuario=request.id_usuario,
      nro_mesa=request.nro_mesa,
      mensaje=request.mensaje
    )

    return {
      "status": "success",
      "mesa": request.nro_mesa,
      "respuesta_ia": respuesta
    }
  except Exception as e:  # Cambiamos ValueError por Exception para atrapar TODO
    import traceback
    print("========= 🚨 ERROR CRÍTICO EN EL CHAT DE AKAZA 🚨 =========")
    print(f"Datos recibidos -> Usuario: {request.id_usuario}, Mesa: {request.nro_mesa}, Mensaje: {request.mensaje}")
    traceback.print_exc()  # Esto pintará las letras rojas exactas en Render
    print("==========================================================")
    raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")