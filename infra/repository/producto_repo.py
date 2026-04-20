from sqlalchemy.orm import Session
from core.schemas.inventario_schema import ProductoCreate
from infra.db.models.inventario import Producto

class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    # Obtener un producto por ID
    def obtener_por_id(self, id_producto: int):
        return self.db.query(Producto).filter(Producto.id == id_producto).first()

    # Obtener todos los productos
    def obtener_todos(self):
        return self.db.query(Producto).all()

    # Crear un nuevo producto
    def crear_producto(self, data: ProductoCreate):
        nuevo_producto = Producto(
            nombre=data.nombre,
            unidad_medida=data.unidad_medida,
            stock_actual=data.stock_actual,
            stock_minimo_alerta=data.stock_minimo_alerta
        )
        self.db.add(nuevo_producto)
        self.db.commit()
        self.db.refresh(nuevo_producto)
        return nuevo_producto

    # Actualizar un producto
    def actualizar_stock(self, id_producto: int, cantidad: float):
        producto = self.obtener_por_id(id_producto)
        if producto:
            producto.stock_actual += cantidad
            self.db.commit()
            self.db.refresh(producto)
        return producto