from sqlalchemy.orm import Session
from core.schemas.inventario_schema import ProductoCreate
from infra.repository.producto_repo import ProductoRepository


class InventarioService:
  def __init__(self, db: Session):
    self.producto_repo = ProductoRepository(db)

  # ==========================================
  # 1. MÉTODOS CRUD ESTÁNDAR
  # ==========================================
  def listar_productos(self):
    return self.producto_repo.obtener_todos()

  def obtener_producto(self, id_producto: int):
    producto = self.producto_repo.obtener_por_id(id_producto)
    if not producto:
      raise ValueError(f"El producto con ID {id_producto} no existe.")
    return producto

  def registrar_producto(self, data: ProductoCreate):
    return self.producto_repo.crear_producto(data)

  def modificar_producto(self, id_producto: int, data: ProductoCreate):
    producto = self.producto_repo.actualizar_producto(id_producto, data)
    if not producto:
      raise ValueError(f"No se pudo actualizar. El producto {id_producto} no existe.")
    return producto

  def borrar_producto(self, id_producto: int):
    producto = self.producto_repo.eliminar_producto(id_producto)
    if not producto:
      raise ValueError(f"No se pudo eliminar. El producto {id_producto} no existe.")
    return {"mensaje": f"Producto {id_producto} eliminado exitosamente."}

  # ==========================================
  # 2. LÓGICA DE NEGOCIO (INVENTARIO E IA)
  # ==========================================
  def mover_stock(self, id_producto: int, cantidad: float):
    """
    Suma o resta stock. 'cantidad' puede ser positiva (cuando compras insumos)
    o negativa (cuando la IA vende un plato o hay merma).
    """
    producto = self.obtener_producto(id_producto)  # Reutilizamos la validación de arriba

    # REGLA DE NEGOCIO: El stock no puede ser negativo
    if producto.stock_actual + cantidad < 0:
      raise ValueError(f"Stock insuficiente para '{producto.nombre}'. "
                       f"Stock actual: {producto.stock_actual}, Intentaste descontar: {abs(cantidad)}")

    return self.producto_repo.actualizar_stock(id_producto, cantidad)

  def obtener_alertas_stock(self) -> list:
    """
    ESTA FUNCIÓN ES ORO PURO PARA TU PROYECTO.
    Devuelve solo los productos que están por agotarse.
    Puedes mostrar esto en el frontend del administrador o enviárselo a la IA
    para que NO ofrezca platos con estos ingredientes.
    """
    productos = self.listar_productos()
    alertas = []

    for p in productos:
      if p.stock_actual <= p.stock_minimo_alerta:
        alertas.append({
          "id_producto": p.id,
          "nombre": p.nombre,
          "stock_actual": float(p.stock_actual),
          "minimo_requerido": float(p.stock_minimo_alerta),
          "estado": "AGOTADO" if p.stock_actual == 0 else "CRÍTICO"
        })

    return alertas