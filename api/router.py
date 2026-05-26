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

  # Normalizar valores ficticios (0) a None para mantener consistencia interna y de BD
  id_usuario_final = request.id_usuario if request.id_usuario != 0 else None
  nro_mesa_final = request.nro_mesa if request.nro_mesa != 0 else None

  try:
    respuesta = chat_service.procesar_mensaje(
      id_usuario=id_usuario_final,
      nro_mesa=nro_mesa_final,
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