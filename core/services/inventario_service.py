from sqlalchemy.orm import Session
from core.schemas.inventario_schema import ProductoCreate, CompraCreate
from infra.repository.producto_repo import ProductoRepository

class InventarioService:
    """Manages raw products, inventory transactions, supply purchases, and alerts."""

    def __init__(self, db: Session):
        self.producto_repo = ProductoRepository(db)

    def listar_productos(self):
        """Lists all cataloged raw ingredients/products."""
        return self.producto_repo.obtener_todos()

    def obtener_producto(self, id_producto: int):
        """Retrieves a single product by identifier."""
        producto = self.producto_repo.obtener_por_id(id_producto)
        if not producto:
            raise ValueError(f"El producto con ID {id_producto} no existe.")
        return producto

    def registrar_producto(self, data: ProductoCreate):
        """Registers a new ingredient/product in stock."""
        return self.producto_repo.crear_producto(data)

    def modificar_producto(self, id_producto: int, data: ProductoCreate):
        """Updates attributes of an existing product."""
        producto = self.producto_repo.actualizar_producto(id_producto, data)
        if not producto:
            raise ValueError(f"No se pudo actualizar. El producto {id_producto} no existe.")
        return producto

    def borrar_producto(self, id_producto: int):
        """Removes a product from catalog."""
        producto = self.producto_repo.eliminar_producto(id_producto)
        if not producto:
            raise ValueError(f"No se pudo eliminar. El producto {id_producto} no existe.")
        return {"mensaje": f"Producto {id_producto} eliminado exitosamente."}

    def registrar_compra(self, data: CompraCreate):
        """
        Registers incoming product shipments.
        
        Logs purchase history, increases product stock, and updates pricing metrics.
        """
        try:
            return self.producto_repo.registrar_compra(data)
        except ValueError as e:
            raise e

    def mover_stock(self, id_producto: int, cantidad: float):
        """
        Performs manual stock adjustments.
        
        Accepts positive numbers for manual ingestion and negative numbers for adjustments.
        """
        producto = self.obtener_producto(id_producto)

        if float(producto.stock_actual) + cantidad < 0:
            raise ValueError(
                f"Stock insuficiente para '{producto.nombre}'. "
                f"Stock actual: {producto.stock_actual}, intentaste descontar: {abs(cantidad)}"
            )
        return self.producto_repo.actualizar_stock(id_producto, cantidad)

    def obtener_alertas_stock(self) -> list:
        """Finds all products where stock_actual is below or equal to stock_minimo_alerta."""
        productos = self.listar_productos()
        return [
            {
                "id_producto": p.id,
                "nombre": p.nombre,
                "stock_actual": float(p.stock_actual),
                "minimo_requerido": float(p.stock_minimo_alerta),
                "estado": "AGOTADO" if p.stock_actual == 0 else "CRÍTICO",
            }
            for p in productos
            if p.stock_actual <= p.stock_minimo_alerta
        ]