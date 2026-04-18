from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Union, Literal
from decimal import Decimal
from datetime import datetime

# ==========================================
# TIPOS ESTRICTOS PARA ESTADOS
# ==========================================
# Solo se aceptan estas palabras exactas.
EstadoCocina = Literal["ESPERA", "PREPARANDO", "LISTO", "ENTREGADO", "CANCELADO"]
EstadoPago = Literal["PENDIENTE", "PAGADO", "ANULADO"]


# ==========================================
# 1. SCHEMAS PARA DETALLE DE PEDIDO
# ==========================================
class DetallePedidoCreate(BaseModel):
  # La IA puede mandar el ID del plato o decir "Lomo Saltado"
  plato_ref: Optional[Union[int, str]] = None
  combo_ref: Optional[Union[int, str]] = None

  cantidad: int = Field(default=1, gt=0)
  nota_personalizacion: Optional[str] = Field(None, description="Ej: Bien cocido, sin sal")

  # Manejo inteligente de sustituciones ("Quítale la cebolla y ponle huevo")
  prod_quitado_ref: Optional[Union[int, str]] = None
  prod_sustituto_ref: Optional[Union[int, str]] = None

  @model_validator(mode='after')
  def validar_plato_o_combo(self):
    # Valida que hayan pedido un plato o un combo, pero no ambos vacíos ni ambos llenos
    if not self.plato_ref and not self.combo_ref:
      raise ValueError("Debes especificar un plato o un combo para el detalle.")
    if self.plato_ref and self.combo_ref:
      raise ValueError("El detalle debe ser un plato o un combo, no ambos a la vez.")
    return self


class DetallePedidoResponse(BaseModel):
  id: int
  id_plato: Optional[int] = None
  id_combo: Optional[int] = None
  cantidad: int
  nota_personalizacion: Optional[str] = None
  id_prod_quitado: Optional[int] = None
  id_prod_sustituto: Optional[int] = None

  class Config:
    from_attributes = True


# ==========================================
# 2. SCHEMAS PARA PEDIDOS (Maestro)
# ==========================================
class PedidoCreate(BaseModel):
  # Opcional porque a veces el cajero crea el pedido sin asignar un usuario registrado
  id_usuario: Optional[int] = None
  nro_mesa: int = Field(..., gt=0)

  # ¡Magia pura! Permite recibir todo el pedido y sus detalles en un solo JSON
  detalles: List[DetallePedidoCreate] = Field(..., min_length=1, description="Lista de platos/combos pedidos")


class PedidoResponse(BaseModel):
  id: int
  id_usuario: Optional[int] = None
  nro_mesa: int
  estado_cocina: EstadoCocina
  estado_pago: EstadoPago
  total: Decimal
  fecha_venta: datetime

  # Devuelve el ticket completo con todo lo que pidieron
  detalles: List[DetallePedidoResponse] = Field(default_factory=list)

  class Config:
    from_attributes = True


# ==========================================
# 3. SCHEMAS PARA RESUMEN DE VENTAS
# ==========================================
# (Generalmente no hay un 'Create' aquí porque esto lo calcula el sistema automáticamente al final del día)

class VentaDiaResumenResponse(BaseModel):
  id: int
  fecha: datetime
  total_recaudado: Decimal
  total_platos_vendidos: int
  merma_total_estimada_gr: Decimal

  class Config:
    from_attributes = True