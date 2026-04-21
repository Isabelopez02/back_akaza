from sqlalchemy.orm import Session
from infra.db.models.chat import IAHistorialChat # Asegúrate de que la ruta sea correcta

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def guardar_interaccion(self, id_usuario: int, mensaje_cliente: str, respuesta_ia: str, contexto: dict, id_pedido: int = None):
        try:
            nueva_interaccion = IAHistorialChat(
                id_usuario=id_usuario,
                id_pedido=id_pedido, # Puede ser nulo si están conversando antes de pedir
                mensaje_cliente=mensaje_cliente,
                respuesta_ia=respuesta_ia,
                contexto_enviado=contexto
            )
            self.db.add(nueva_interaccion)
            self.db.commit()
            self.db.refresh(nueva_interaccion)
            return nueva_interaccion
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al guardar el historial del chat: {str(e)}")