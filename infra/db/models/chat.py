from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from infra.db.database import Base


class IAHistorialChat(Base):
    __tablename__ = "ia_historial_chat"

    id = Column(Integer, primary_key=True, index=True)

    id_usuario = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))
    id_pedido = Column(Integer, ForeignKey("pedidos.id", ondelete="SET NULL"), nullable=True)

    mensaje_cliente = Column(Text, nullable=False)
    respuesta_ia = Column(Text, nullable=False)

    contexto_enviado = Column(JSONB)

    fecha_interaccion = Column(TIMESTAMP, default=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario")
    pedido = relationship("Pedido")