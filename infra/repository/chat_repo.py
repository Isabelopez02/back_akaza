from sqlalchemy.orm import Session
from infra.db.models.chat import IAHistorialChat # Asegúrate de que la ruta sea correcta

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def guardar_interaccion(self, id_usuario: int, mensaje_cliente: str,nro_mesa: int, respuesta_ia: str, contexto: dict, id_pedido: int = None):
        try:
            usuario_final = id_usuario if id_usuario > 0 else None
            nueva_interaccion = IAHistorialChat(
                id_usuario=usuario_final,
                id_pedido=id_pedido, # Puede ser nulo si están conversando antes de pedir
                nro_mesa=nro_mesa,
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

    def obtener_historial_reciente(self, id_usuario: int, nro_mesa: int, limite: int = 5):
        try:
            # Buscamos los últimos mensajes del usuario
            # Asumimos que tu modelo IAHistorialChat tiene una columna 'id' autoincremental
            # Si tienes una columna de fecha (ej. 'fecha_creacion'), puedes usar esa en el order_by
            historial = self.db.query(IAHistorialChat) \
                .filter(IAHistorialChat.id_usuario == id_usuario) \
                .order_by(IAHistorialChat.id.desc()) \
                .limit(limite) \
                .all()

            # Devolvemos la lista en orden cronológico (del más antiguo al más nuevo de esos 5)
            return list(reversed(historial))

        except Exception as e:
            raise ValueError(f"Error al obtener el historial del chat: {str(e)}")