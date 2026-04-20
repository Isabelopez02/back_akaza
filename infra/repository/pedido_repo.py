from sqlalchemy.orm import Session
from core.schemas.venta_schema import PedidoCreate
from infra.db.models.ventas import Pedido, DetallePedido

class PedidoRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear_pedido(self,  data: PedidoCreate):
        # 1. Crear la cabecera del pedido
        nuevo_pedido = Pedido(
            id_usuario=data.id_usuario,
            nro_mesa=data.nro_mesa,
            estado_cocina="ESPERA",
            estado_pago="PENDIENTE",
            total=0.0  # El total se puede calcular en un segundo paso o servicio
        )
        self.db.add(nuevo_pedido)
        self.db.flush()  # Genera el ID sin hacer commit todavía

        # 2. Crear cada detalle (platos/combos pedidos)
        for item in data.detalles:
            nuevo_detalle = DetallePedido(
                id_pedido=nuevo_pedido.id,
                # Guardamos la referencia tal cual la manda el frontend
                id_plato=item.plato_ref if isinstance(item.plato_ref, int) else None,
                id_combo=item.combo_ref if isinstance(item.combo_ref, int) else None,
                cantidad=item.cantidad,
                nota_personalizacion=item.nota_personalizacion
            )
            self.db.add(nuevo_detalle)

        self.db.commit()
        self.db.refresh(nuevo_pedido)
        return nuevo_pedido

    def obtener_pedido_por_id(self, id_pedido: int):
        return self.db.query(Pedido).filter(Pedido.id == id_pedido).first()

    def listar_pedidos_por_mesa(self, nro_mesa: int):
        return self.db.query(Pedido).filter(Pedido.nro_mesa == nro_mesa).all()