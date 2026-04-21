from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from infra.db.database import get_db
from core.schemas.chat import ChatRequest  # Importa tu schema
from core.services.chatbot import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chatbot IA - Akaza"])


@router.post("/mensaje")
def hablar_con_akaza(request: ChatRequest, db: Session = Depends(get_db)):
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
  except ValueError as e:
    raise HTTPException(status_code=500, detail=str(e))