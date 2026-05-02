from pydantic import BaseModel, Field, model_validator
from typing import Optional, Union
from decimal import Decimal
from datetime import datetime

# ==========================================
# 1. SCHEMAS PARA PRODUCTOS (Inventario)
# ==========================================
class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    unidad_medida: str = Field(..., min_length=1, max_length=20, description="Ej: kg, litro, unidad")
    stock_minimo_alerta: Decimal = Field(..., ge=0)


class ProductoCreate(ProductoBase):
    # El stock actual es opcional al crearlo (puede empezar en 0)
    stock_actual: Decimal = Field(default=Decimal("0.00"), ge=0)
    # Precio inicial de compra (opcional; registra también en compras_historial si se pasa)
    precio_compra: Optional[Decimal] = Field(default=None, ge=0)
    # Mermas estimadas (opcionales; si se pasan, se insertan en mermas_estimadas)
    merma_min_porcentaje: Optional[Decimal] = Field(default=None, ge=0, le=100)
    merma_max_porcentaje: Optional[Decimal] = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def validar_merma(self):
        mn = self.merma_min_porcentaje
        mx = self.merma_max_porcentaje
        if mn is not None and mx is not None and mn > mx:
            raise ValueError("La merma mínima no puede ser mayor a la máxima")
        return self


class ProductoResponse(ProductoBase):
    id: int
    stock_actual: Decimal
    precio_compra: Optional[Decimal] = None
    # Precio de la penúltima compra → permite indicador visual de alza en el frontend
    precio_compra_anterior: Optional[Decimal] = None
    merma_min_porcentaje: Optional[Decimal] = None
    merma_max_porcentaje: Optional[Decimal] = None

    class Config:
        from_attributes = True


# ==========================================
# 2. SCHEMA PARA REGISTRAR UNA COMPRA
# POST /api/compras → registra en compras_historial,
# suma stock al producto y actualiza su precio_compra.
# ==========================================
class CompraCreate(BaseModel):
    id_producto: int = Field(..., description="ID del producto que se está comprando")
    cantidad: Decimal = Field(..., gt=0, description="Cantidad comprada (ej: 5, 2.5)")
    unidad_medida: str = Field(..., min_length=1, max_length=20, description="Unidad de esta compra")
    precio_unitario: Decimal = Field(..., gt=0, description="Precio por unidad/kg/litro pagado")


class CompraResponse(BaseModel):
    id: int
    id_producto: int
    cantidad_comprada: Decimal
    unidad_medida: str
    precio_unidad_compra: Decimal
    fecha_compra: datetime
    # Producto actualizado embebido → el frontend lo usa para actualizar la tarjeta sin re-fetch
    producto: ProductoResponse

    class Config:
        from_attributes = True


# ==========================================
# 3. SCHEMAS LEGACY PARA HISTORIAL DE COMPRAS
# ==========================================
class CompraHistorialCreate(BaseModel):
    producto_ref: Union[int, str] = Field(..., description="ID o Nombre del producto comprado")
    cantidad_comprada: Decimal = Field(..., gt=0)
    precio_unidad_compra: Decimal = Field(..., gt=0)


class CompraHistorialResponse(BaseModel):
    id: int
    id_producto: int
    cantidad_comprada: Decimal
    precio_unidad_compra: Decimal
    fecha_compra: datetime

    class Config:
        from_attributes = True


# ==========================================
# 4. SCHEMAS PARA MERMAS ESTIMADAS
# ==========================================
class MermaEstimadaCreate(BaseModel):
    producto_ref: Union[int, str] = Field(..., description="ID o Nombre del producto")
    merma_min_porcentaje: Decimal = Field(..., ge=0, le=100)
    merma_max_porcentaje: Decimal = Field(..., ge=0, le=100)

    @model_validator(mode="after")
    def validar_rango(self):
        if self.merma_min_porcentaje > self.merma_max_porcentaje:
            raise ValueError("La merma mínima no puede ser mayor a la máxima")
        return self


class MermaEstimadaResponse(BaseModel):
    id_producto: int
    merma_min_porcentaje: Decimal
    merma_max_porcentaje: Decimal

    class Config:
        from_attributes = True