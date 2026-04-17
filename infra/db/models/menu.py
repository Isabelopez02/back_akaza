from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from infra.db.database import Base


class Plato(Base):
    __tablename__ = "platos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    precio_venta = Column(DECIMAL(10, 2))

    recetas = relationship("Receta", back_populates="plato")
    detalles_pedido = relationship("DetallePedido", back_populates="plato")


class Receta(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True)
    id_plato = Column(Integer, ForeignKey("platos.id"))
    id_producto = Column(Integer, ForeignKey("productos.id"))
    cantidad_estimada = Column(DECIMAL(10, 2))
    unidad_medida = Column(String(20))
    es_opcional = Column(Boolean, default=False)

    plato = relationship("Plato", back_populates="recetas")
    producto = relationship("Producto")


class Combo(Base):
    __tablename__ = "combos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    precio_venta = Column(DECIMAL(10, 2))
    activo = Column(Boolean, default=True)

    platos = relationship("ComboPlato", back_populates="combo")
    detalles_pedido = relationship("DetallePedido", back_populates="combo")


class ComboPlato(Base):
    __tablename__ = "combo_platos"

    id_combo = Column(Integer, ForeignKey("combos.id"), primary_key=True)
    id_plato = Column(Integer, ForeignKey("platos.id"), primary_key=True)

    combo = relationship("Combo", back_populates="platos")
    plato = relationship("Plato")


class SustitucionPermitida(Base):
    __tablename__ = "sustituciones_permitidas"

    id = Column(Integer, primary_key=True)
    id_producto_original = Column(Integer, ForeignKey("productos.id"))
    id_producto_nuevo = Column(Integer, ForeignKey("productos.id"))
    costo_adicional = Column(DECIMAL(10, 2), default=0.00)

    producto_original = relationship("Producto", foreign_keys=[id_producto_original])
    producto_nuevo = relationship("Producto", foreign_keys=[id_producto_nuevo])