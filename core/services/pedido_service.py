from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from core.schemas.venta_schema import PedidoCreate
from infra.repository.pedido_repo import PedidoRepository


class PedidoService:
  def __init__(self, db: Session):
    self.pedido_repo = PedidoRepository(db)

  def registrar_nuevo_pedido(self, data: PedidoCreate):
    """
    Lógica Principal de la IA al tomar la orden.
    """
    # ========================================================
    # REGLA DE NEGOCIO 1: EL CANDADO DE LOS 5 MINUTOS
    # ========================================================
    # Obtenemos todos los pedidos de esta mesa
    pedidos_mesa = self.pedido_repo.listar_pedidos_por_mesa(data.nro_mesa)

    if pedidos_mesa:
      # Tomamos el último pedido registrado para esta mesa
      ultimo_pedido = pedidos_mesa[-1]

      # Verificamos si tiene el campo de fecha (asegúrate de que en tu BD se llame 'fecha_venta' o cámbialo aquí)
      if hasattr(ultimo_pedido, 'fecha_venta') and ultimo_pedido.fecha_venta:
        tiempo_transcurrido = datetime.now() - ultimo_pedido.fecha_venta

        # Si han pasado MENOS de 5 minutos, bloqueamos el nuevo pedido
        if tiempo_transcurrido < timedelta(minutes=5):
          minutos_restantes = 5 - (tiempo_transcurrido.seconds // 60)
          raise ValueError(f"Conflicto de concurrencia: Ya se está procesando un pedido en la mesa {data.nro_mesa}. "
                           f"La IA debe pedirle al cliente que espere {minutos_restantes} minuto(s).")

    # ========================================================
    # REGLA DE NEGOCIO 2: CREACIÓN DEL PEDIDO
    # ========================================================
    try:
      # Si pasamos el candado de tiempo, mandamos a crear el pedido al Repositorio.
      # OJO: La IA lo creará en estado "ESPERA" o "BORRADOR" según lo definas en tu BD.
      nuevo_pedido = self.pedido_repo.crear_pedido(data)
      return nuevo_pedido

    except Exception as e:
      raise ValueError(f"Error interno al procesar el pedido en la BD: {str(e)}")

  # ========================================================
  # FUNCIONES DE LECTURA Y ACTUALIZACIÓN
  # ========================================================
  def obtener_pedido(self, id_pedido: int):
    pedido = self.pedido_repo.obtener_pedido_por_id(id_pedido)
    if not pedido:
      raise ValueError(f"El pedido {id_pedido} no existe.")
    return pedido

  def listar_pedidos_mesa(self, nro_mesa: int):
    return self.pedido_repo.listar_pedidos_por_mesa(nro_mesa)

  def confirmar_pedido_ia(self, id_pedido: int):
    """
    Esta es la función que la IA llama cuando pregunta: "¿Todos están de acuerdo?"
    y el cliente dice "Sí". Automáticamente lo manda a la cola de la cocina.
    """
    pedido_actualizado = self.pedido_repo.actualizar_estado(
      id_pedido=id_pedido,
      estado_cocina="PREPARANDO",  # ¡Entra a la cocina!
      estado_pago="PENDIENTE"
    )
    return pedido_actualizado

  def cancelar_o_anular_pedido(self, id_pedido: int):
    """
    Por si el cliente se arrepiente antes de que empiece a cocinarse.
    """
    return self.pedido_repo.actualizar_estado(id_pedido, "CANCELADO", "ANULADO")