from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from infra.db.database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Si es null, es "Clientes Varios"
    nro_mesa = Column(Integer)
    estado_cocina = Column(String(50), default="ESPERA")
    estado_pago = Column(String(50), default="PENDIENTE")
    ticket = Column(String(50), nullable=True) # Ej: ORD-1001
    total = Column(DECIMAL(10, 2))
    fecha_venta = Column(TIMESTAMP, default=datetime.utcnow)

    usuario = relationship("Usuario")
    detalles = relationship("DetallePedido", back_populates="pedido")
    comprobante = relationship("CompraCliente", back_populates="pedido", uselist=False)


class CompraCliente(Base):
    __tablename__ = "compras_clientes"

    id = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id"), unique=True)
    ticket = Column(String(50))
    total = Column(DECIMAL(10, 2))
    metodo_pago = Column(String(50), default="EFECTIVO")
    monto_efectivo = Column(DECIMAL(10, 2), default=0.0)
    monto_yape = Column(DECIMAL(10, 2), default=0.0)
    monto_tarjeta = Column(DECIMAL(10, 2), default=0.0)
    fecha_pago = Column(TIMESTAMP, default=datetime.utcnow)

    pedido = relationship("Pedido", back_populates="comprobante")


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