from typing import Optional

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    id_usuario: Optional[int] = Field(None, description="ID del usuario si hizo login")
    nro_mesa: Optional[int] = Field(None, description="Mesa si escaneó el QR")
    mensaje: str = Field(..., min_length=1, description="Lo que el cliente le dijo a la IA")