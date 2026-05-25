from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from core.schemas.venta_schema import PedidoCreate
from infra.repository.pedido_repo import PedidoRepository

class PedidoService:
  """Orquesta las operaciones de los pedidos, incluyendo reglas de validación y procesamiento de pagos."""

  def __init__(self, db: Session):
    self.pedido_repo = PedidoRepository(db)

  def registrar_nuevo_pedido(self, data: PedidoCreate):
    """
    Valida límites de concurrencia y almacena un nuevo pedido de cliente.
    
    Incluye una restricción de concurrencia por mesa para evitar entradas duplicadas.
    """
    pedidos_mesa = self.pedido_repo.listar_pedidos_por_mesa(data.nro_mesa)

    if pedidos_mesa:
      ultimo_pedido = pedidos_mesa[-1]

      if hasattr(ultimo_pedido, 'fecha_venta') and ultimo_pedido.fecha_venta:
        tiempo_transcurrido = datetime.utcnow() - ultimo_pedido.fecha_venta

        # Guardia de concurrencia: bloquea envíos duplicados de la misma mesa en menos de 2 segundos
        if tiempo_transcurrido < timedelta(seconds=2):
          raise ValueError(
              f"Conflicto de concurrencia: Ya se está procesando un pedido en la mesa {data.nro_mesa}. "
              "Por favor, espera un momento antes de reintentar."
          )

    try:
      # Por defecto se establece en estado PENDING o ESPERA durante la ingesta
      nuevo_pedido = self.pedido_repo.crear_pedido(data)
      return nuevo_pedido
    except Exception as e:
      raise ValueError(f"Error interno al procesar el pedido en la BD: {str(e)}")

  def obtener_pedido(self, id_pedido: int):
    """Obtiene los detalles de un único pedido por su identificador."""
    pedido = self.pedido_repo.obtener_pedido_por_id(id_pedido)
    if not pedido:
      raise ValueError(f"El pedido {id_pedido} no existe.")
    return pedido

  def listar_pedidos_mesa(self, nro_mesa: int):
    """Lista todos los pedidos creados para un número de mesa específico."""
    return self.pedido_repo.listar_pedidos_por_mesa(nro_mesa)

  def listar_todos_pedidos(self):
    """Lista todos los pedidos históricos y activos en la base de datos."""
    return self.pedido_repo.listar_todos_pedidos()

  def confirmar_pedido_ia(self, id_pedido: int):
    """Envía un borrador de pedido pendiente directamente a la cola de preparación de la cocina."""
    pedido_actualizado = self.pedido_repo.actualizar_estado(
      id_pedido=id_pedido,
      estado_cocina="PREPARANDO",
      estado_pago="PENDIENTE"
    )
    return pedido_actualizado

  def cancelar_o_anular_pedido(self, id_pedido: int):
    """Cancela o anula un pedido antes de que comience la preparación o la ejecución en cocina."""
    return self.pedido_repo.actualizar_estado(id_pedido, "CANCELADO", "ANULADO")

  def pagar_pedido(self, id_pedido: int, metodo_pago: str = "EFECTIVO", 
                   monto_efectivo: float = 0.0, monto_yape: float = 0.0, monto_tarjeta: float = 0.0,
                   ticket_pago: str = None):
    """Marca un pedido como pagado y crea el registro de CompraCliente correspondiente."""
    pedido_pagado = self.pedido_repo.pagar_pedido(
        id_pedido, metodo_pago, 
        monto_efectivo, monto_yape, monto_tarjeta, 
        ticket_pago
    )
    if not pedido_pagado:
      raise ValueError(f"El pedido {id_pedido} no pudo ser pagado o ya está pagado.")
    return pedido_pagado