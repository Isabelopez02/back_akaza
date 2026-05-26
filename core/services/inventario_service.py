from sqlalchemy.orm import Session
from core.schemas.inventario_schema import ProductoCreate, CompraCreate
from infra.repository.producto_repo import ProductoRepository

class InventarioService:
    """Gestiona los productos crudos, transacciones de inventario, compras de abastecimiento y alertas."""

    def __init__(self, db: Session):
        self.producto_repo = ProductoRepository(db)

    def listar_productos(self):
        """Lista todos los ingredientes crudos o productos catalogados."""
        return self.producto_repo.obtener_todos()

    def obtener_producto(self, id_producto: int):
        """Obtiene un único producto por su identificador."""
        producto = self.producto_repo.obtener_por_id(id_producto)
        if not producto:
            raise ValueError(f"El producto con ID {id_producto} no existe.")
        return producto

    def registrar_producto(self, data: ProductoCreate):
        """Registra un nuevo ingrediente/producto en stock."""
        return self.producto_repo.crear_producto(data)

    def modificar_producto(self, id_producto: int, data: ProductoCreate):
        """Actualiza los atributos de un producto existente."""
        producto = self.producto_repo.actualizar_producto(id_producto, data)
        if not producto:
            raise ValueError(f"No se pudo actualizar. El producto {id_producto} no existe.")
        return producto

    def borrar_producto(self, id_producto: int):
        """Elimina un producto del catálogo."""
        producto = self.producto_repo.eliminar_producto(id_producto)
        if not producto:
            raise ValueError(f"No se pudo eliminar. El producto {id_producto} no existe.")
        return {"mensaje": f"Producto {id_producto} eliminado exitosamente."}

    def registrar_compra(self, data: CompraCreate):
        """
        Registra los envíos de productos entrantes.
        
        Registra el historial de compras, incrementa el stock de productos y actualiza las métricas de precios.
        """
        try:
            return self.producto_repo.registrar_compra(data)
        except ValueError as e:
            raise e

    def mover_stock(self, id_producto: int, cantidad: float):
        """
        Realiza ajustes de stock manuales.
        
        Acepta números positivos para el ingreso manual y números negativos para los ajustes de descuento.
        """
        producto = self.obtener_producto(id_producto)

        if float(producto.stock_actual) + cantidad < 0:
            raise ValueError(
                f"Stock insuficiente para '{producto.nombre}'. "
                f"Stock actual: {producto.stock_actual}, intentaste descontar: {abs(cantidad)}"
            )
        return self.producto_repo.actualizar_stock(id_producto, cantidad)

    def obtener_alertas_stock(self) -> list:
        """Encuentra todos los productos donde el stock_actual es menor o igual a stock_minimo_alerta."""
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