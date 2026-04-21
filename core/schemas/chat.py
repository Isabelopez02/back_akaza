from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    id_usuario: int = Field(..., description="ID del usuario logueado")
    nro_mesa: int = Field(..., gt=0, description="Mesa desde donde escribe")
    mensaje: str = Field(..., min_length=1, description="Lo que el cliente le dijo a la IA")