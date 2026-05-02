from decimal import Decimal
from sqlalchemy.orm import Session
from core.schemas.inventario_schema import ProductoCreate, CompraCreate
from infra.db.models.inventario import Producto, CompraHistorial, MermaEstimada


class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    # ─── Helpers ───────────────────────────────────────────────────────────────

    def _enriquecer(self, producto: Producto) -> Producto:
        """Adjunta campos de merma al objeto ORM para que Pydantic los serialice."""
        merma = (
            self.db.query(MermaEstimada)
            .filter(MermaEstimada.id_producto == producto.id)
            .first()
        )
        producto.merma_min_porcentaje = merma.merma_min_porcentaje if merma else None
        producto.merma_max_porcentaje = merma.merma_max_porcentaje if merma else None
        return producto

    # ─── Lecturas ──────────────────────────────────────────────────────────────

    def obtener_por_id(self, id_producto: int) -> Producto | None:
        return self.db.query(Producto).filter(Producto.id == id_producto).first()

    def obtener_todos(self) -> list[Producto]:
        productos = self.db.query(Producto).all()
        return [self._enriquecer(p) for p in productos]

    # ─── Crear producto ────────────────────────────────────────────────────────

    def crear_producto(self, data: ProductoCreate) -> Producto:
        nuevo = Producto(
            nombre=data.nombre,
            unidad_medida=data.unidad_medida,
            stock_actual=data.stock_actual,
            stock_minimo_alerta=data.stock_minimo_alerta,
            precio_compra=data.precio_compra,
            precio_compra_anterior=None,
        )
        self.db.add(nuevo)
        self.db.flush()  # Obtener ID sin commit todavía

        # Mermas estimadas (opcional)
        if data.merma_min_porcentaje is not None and data.merma_max_porcentaje is not None:
            self.db.add(MermaEstimada(
                id_producto=nuevo.id,
                merma_min_porcentaje=data.merma_min_porcentaje,
                merma_max_porcentaje=data.merma_max_porcentaje,
            ))

        # Si se pasó precio_compra inicial, registrar en historial
        if data.precio_compra is not None and data.stock_actual > 0:
            self.db.add(CompraHistorial(
                id_producto=nuevo.id,
                cantidad_comprada=data.stock_actual,
                unidad_medida=data.unidad_medida,
                precio_unidad_compra=data.precio_compra,
            ))

        self.db.commit()
        self.db.refresh(nuevo)
        return self._enriquecer(nuevo)

    # ─── Registrar una compra (el core del módulo) ─────────────────────────────

    def registrar_compra(self, data: CompraCreate) -> tuple[CompraHistorial, Producto]:
        """
        Lógica atómica de compra:
        1. Guarda precio actual → precio_compra_anterior
        2. Actualiza precio_compra con el nuevo precio
        3. Suma la cantidad al stock
        4. Inserta en compras_historial
        Todo en una sola transacción.
        """
        producto = self.obtener_por_id(data.id_producto)
        if not producto:
            raise ValueError(f"Producto {data.id_producto} no encontrado")

        # Rotar precios: actual → anterior, nuevo → actual
        if producto.precio_compra is not None:
            producto.precio_compra_anterior = producto.precio_compra
        producto.precio_compra = data.precio_unitario

        # Sumar stock
        producto.stock_actual = (producto.stock_actual or Decimal("0")) + data.cantidad

        # Registrar en historial
        registro = CompraHistorial(
            id_producto=producto.id,
            cantidad_comprada=data.cantidad,
            unidad_medida=data.unidad_medida,
            precio_unidad_compra=data.precio_unitario,
        )
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(producto)
        self.db.refresh(registro)

        return registro, self._enriquecer(producto)

    # ─── Stock manual ──────────────────────────────────────────────────────────

    def actualizar_stock(self, id_producto: int, cantidad: float) -> Producto | None:
        producto = self.obtener_por_id(id_producto)
        if producto:
            producto.stock_actual += Decimal(str(cantidad))
            self.db.commit()
            self.db.refresh(producto)
            return self._enriquecer(producto)
        return None

    # ─── Actualizar producto completo ──────────────────────────────────────────

    def actualizar_producto(self, id_producto: int, data: ProductoCreate) -> Producto | None:
        producto = self.obtener_por_id(id_producto)
        if producto:
            producto.nombre = data.nombre
            producto.unidad_medida = data.unidad_medida
            producto.stock_actual = data.stock_actual
            producto.stock_minimo_alerta = data.stock_minimo_alerta
            if data.precio_compra is not None:
                if producto.precio_compra is not None:
                    producto.precio_compra_anterior = producto.precio_compra
                producto.precio_compra = data.precio_compra
            self.db.commit()
            self.db.refresh(producto)
            return self._enriquecer(producto)
        return None

    # ─── Eliminar ──────────────────────────────────────────────────────────────

    def eliminar_producto(self, id_producto: int) -> Producto | None:
        producto = self.obtener_por_id(id_producto)
        if producto:
            self.db.delete(producto)
            self.db.commit()
        return producto