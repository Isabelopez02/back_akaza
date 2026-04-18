from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


# ==========================================
# SCHEMAS PARA EL HISTORIAL DEL CHATBOT
# ==========================================
class IAHistorialChatBase(BaseModel):
  id_usuario: int
  id_pedido: Optional[int] = None

  mensaje_cliente: str = Field(..., description="Lo que escribió exactamente el usuario")
  respuesta_ia: str = Field(..., description="Lo que respondió el modelo (OpenAI/Claude/etc)")

  # Dict[str, Any] es el equivalente perfecto para tu JSONB de PostgreSQL
  contexto_enviado: Optional[Dict[str, Any]] = Field(
    default={},
    description="El menú, reglas o datos extra que se le inyectó a la IA en ese turno"
  )


class IAHistorialChatCreate(IAHistorialChatBase):
  pass


class IAHistorialChatResponse(IAHistorialChatBase):
  id: int
  fecha_interaccion: datetime

  class Config:
    from_attributes = True