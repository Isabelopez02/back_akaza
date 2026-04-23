from sqlalchemy.orm import Session
from core.schemas.venta_schema import PedidoCreate
from infra.db.models.ventas import Pedido, DetallePedido
from infra.db.models.menu import Plato


class PedidoRepository:
  def __init__(self, db: Session):
    self.db = db

  def crear_pedido(self, data: PedidoCreate):
    try:
      total_pedido = 0.0

      # 1. Crear cabecera del pedido
      nuevo_pedido = Pedido(
        id_usuario=data.id_usuario,
        nro_mesa=data.nro_mesa,
        estado_cocina="ESPERA",
        estado_pago="PENDIENTE",
        total=0.0
      )
      self.db.add(nuevo_pedido)
      self.db.flush()  # Flush obtiene el ID del pedido sin hacer commit definitivo

      # 2. Procesar cada detalle y sumar el total automáticamente
      for item in data.detalles:
        precio_unitario = 0.0
        id_plato_final = None  # Variable para guardar el ID real del plato

        # Buscamos el precio y el ID real solo si viene plato_ref
        if item.plato_ref:
          plato = None
          if isinstance(item.plato_ref, int):
            plato = self.db.query(Plato).filter(Plato.id == item.plato_ref).first()
          elif isinstance(item.plato_ref, str):
            plato = self.db.query(Plato).filter(Plato.nombre == item.plato_ref).first()

          if plato:
            precio_unitario = float(plato.precio_venta)
            id_plato_final = plato.id  # CORRECCIÓN 1: Capturamos el ID real de la BD

        # Lógica similar para el combo si lo enviaran
        id_combo_final = item.combo_ref if isinstance(item.combo_ref, int) else None

        # Creamos el detalle en BD
        nuevo_detalle = DetallePedido(
          id_pedido=nuevo_pedido.id,
          id_plato=id_plato_final,  # Usamos la variable con el ID real
          id_combo=id_combo_final,
          cantidad=item.cantidad,
          nota_personalizacion=item.nota_personalizacion,

          # CORRECCIÓN 2: Agregamos los campos de sustitución para que no se pierdan
          id_prod_quitado=item.prod_quitado_ref if isinstance(item.prod_quitado_ref, int) else None,
          id_prod_sustituto=item.prod_sustituto_ref if isinstance(item.prod_sustituto_ref, int) else None
        )
        self.db.add(nuevo_detalle)

        # 💰 Sumamos al total general
        total_pedido += (precio_unitario * item.cantidad)

      # Guardamos el total calculado en la cabecera
      nuevo_pedido.total = total_pedido
      self.db.commit()
      self.db.refresh(nuevo_pedido)
      return nuevo_pedido

    except Exception as e:
      self.db.rollback()
      raise e

  def obtener_pedido_por_id(self, id_pedido: int):
    return self.db.query(Pedido).filter(Pedido.id == id_pedido).first()

  def listar_pedidos_por_mesa(self, nro_mesa: int):
    return self.db.query(Pedido).filter(Pedido.nro_mesa == nro_mesa).all()

  def actualizar_estado(self, id_pedido: int, estado_cocina: str, estado_pago: str):
    pedido = self.obtener_pedido_por_id(id_pedido)
    if pedido:
      pedido.estado_cocina = estado_cocina
      pedido.estado_pago = estado_pago
      self.db.commit()
      self.db.refresh(pedido)
    return pedido

  def eliminar_pedido(self, id_pedido: int):
    pedido = self.obtener_pedido_por_id(id_pedido)
    if pedido:
      self.db.delete(pedido)
      self.db.commit()
      return True
    return False