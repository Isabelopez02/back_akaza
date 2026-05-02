from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, TIMESTAMP, Boolean
from datetime import datetime
from infra.db.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    unidad_medida = Column(String(20))
    # Precio actual (se actualiza con cada compra)
    precio_compra = Column(DECIMAL(10, 2), nullable=True)
    # Precio de la penúltima compra (para detectar alza de precio)
    precio_compra_anterior = Column(DECIMAL(10, 2), nullable=True)
    stock_actual = Column(DECIMAL(10, 2), default=0)
    stock_minimo_alerta = Column(DECIMAL(10, 2))


class CompraHistorial(Base):
    __tablename__ = "compras_historial"

    id = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey("productos.id"))
    cantidad_comprada = Column(DECIMAL(10, 2))
    # Unidad usada en esta compra (ej: "kg", "litro", "unidad")
    unidad_medida = Column(String(20))
    precio_unidad_compra = Column(DECIMAL(10, 2))
    fecha_compra = Column(TIMESTAMP, default=datetime.utcnow)


class MermaEstimada(Base):
    __tablename__ = "mermas_estimadas"

    id_producto = Column(Integer, ForeignKey("productos.id"), primary_key=True)
    merma_min_porcentaje = Column(DECIMAL(5, 2))
    merma_max_porcentaje = Column(DECIMAL(5, 2))