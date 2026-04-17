from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from infra.db.database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    nro_mesa = Column(Integer)
    estado_cocina = Column(String(50), default="ESPERA")
    estado_pago = Column(String(50), default="PENDIENTE")
    total = Column(DECIMAL(10, 2))
    fecha_venta = Column(TIMESTAMP, default=datetime.utcnow)

    usuario = relationship("Usuario")
    detalles = relationship("DetallePedido", back_populates="pedido")


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id"))
    id_plato = Column(Integer, ForeignKey("platos.id"), nullable=True)
    id_combo = Column(Integer, ForeignKey("combos.id"), nullable=True)
    cantidad = Column(Integer, default=1)
    nota_personalizacion = Column(String)

    id_prod_quitado = Column(Integer, ForeignKey("productos.id"), nullable=True)
    id_prod_sustituto = Column(Integer, ForeignKey("productos.id"), nullable=True)

    pedido = relationship("Pedido", back_populates="detalles")
    plato = relationship("Plato", back_populates="detalles_pedido")
    combo = relationship("Combo", back_populates="detalles_pedido")

    producto_quitado = relationship("Producto", foreign_keys=[id_prod_quitado])
    producto_sustituto = relationship("Producto", foreign_keys=[id_prod_sustituto])


class VentaDiaResumen(Base):
    __tablename__ = "venta_dia_resumen"

    id = Column(Integer, primary_key=True)
    fecha = Column(TIMESTAMP, unique=True, default=datetime.utcnow)
    total_recaudado = Column(DECIMAL(10, 2))
    total_platos_vendidos = Column(Integer)
    merma_total_estimada_gr = Column(DECIMAL(10, 2))