from pydantic import BaseModel, Field, model_validator
from typing import Optional, Union
from decimal import Decimal
from datetime import datetime

# ==========================================
# 1. SCHEMAS PARA PRODUCTOS (Inventario)
# ==========================================
class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    unidad_medida: str = Field(..., min_length= 1, max_length=20, description="Ej: kg, litro, unidad")
    # ge=0 asegura que nunca configures un stock mínimo negativo
    stock_minimo_alerta: Decimal = Field(..., ge=0)

class ProductoCreate(ProductoBase):
    # El stock actual es opcional al crearlo (puede empezar en 0)
    stock_actual: Decimal = Field(default=Decimal("0.00"), ge=0)

class ProductoResponse(ProductoBase):
    id: int
    stock_actual: Decimal

    class Config:
        from_attributes = True

# ==========================================
# 2. SCHEMAS PARA HISTORIAL DE COMPRAS
# ==========================================
class CompraHistorialCreate(BaseModel):
    # La IA o el usuario pueden enviar el ID (4) o el nombre ("Tomate")
    producto_ref: Union[int, str] = Field(..., description="ID o Nombre del producto comprado")
    # gt=0: Tiene que ser mayor a 0 (no puedes comprar 0 kg ni a 0 soles)
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
# 3. SCHEMAS PARA MERMAS ESTIMADAS
# ==========================================
class MermaEstimadaCreate(BaseModel):
    producto_ref: Union[int, str] = Field(..., description="ID o Nombre del producto")
    # Validamos que el porcentaje esté entre 0 y 100 (le=100 significa Less or Equal a 100)
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