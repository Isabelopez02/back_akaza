from sqlalchemy.orm import Session
from infra.db.models.chat import IAHistorialChat


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def guardar_interaccion(
        self,
        id_usuario: int,
        mensaje_cliente: str,
        nro_mesa: int,
        respuesta_ia: str,
        contexto: dict,
        id_pedido: int = None
    ):
        try:
            # ✅ Validaciones correctas (SIN errores)
            usuario_final = id_usuario if id_usuario is not None else None
            mesa_final = nro_mesa if nro_mesa is not None else None

            nueva_interaccion = IAHistorialChat(
                id_usuario=usuario_final,
                id_pedido=id_pedido,
                nro_mesa=mesa_final,
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
            query = self.db.query(IAHistorialChat)

            # ✅ Soporta usuario O mesa
            if id_usuario is not None:
                query = query.filter(IAHistorialChat.id_usuario == id_usuario)
            elif nro_mesa is not None:
                query = query.filter(IAHistorialChat.nro_mesa == nro_mesa)

            historial = query.order_by(IAHistorialChat.id.desc()).limit(limite).all()

            return list(reversed(historial))

        except Exception as e:
            raise ValueError(f"Error al obtener el historial del chat: {str(e)}")