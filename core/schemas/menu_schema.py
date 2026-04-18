from pydantic import BaseModel, Field
from typing import Optional, List, Union
from decimal import Decimal

# ==========================================
# 1. SCHEMAS PARA SUSTITUCIONES
# ==========================================
class SustitucionCreate(BaseModel):
    producto_original_ref: Union[int, str] = Field(..., description="ID o Nombre del producto a quitar")
    producto_nuevo_ref: Union[int, str] = Field(..., description="ID o Nombre del producto a poner")
    costo_adicional: Decimal = Field(default=Decimal("0.00"), ge=0)

class SustitucionResponse(BaseModel):
    id: int
    id_producto_original: int
    id_producto_nuevo: int
    costo_adicional: Decimal

    class Config:
        from_attributes = True


# ==========================================
# 2. SCHEMAS PARA RECETAS (Ingredientes)
# ==========================================
class RecetaCreate(BaseModel):
    producto_ref: Union[int, str] = Field(..., description="ID o Nombre del ingrediente")
    cantidad_estimada: Decimal = Field(..., gt=0)
    unidad_medida: str = Field(..., max_length=20)
    es_opcional: bool = False

class RecetaResponse(BaseModel):
    id: int
    id_plato: int
    id_producto: int
    cantidad_estimada: Decimal
    unidad_medida: str
    es_opcional: bool

    class Config:
        from_attributes = True


# ==========================================
# 3. SCHEMAS PARA PLATOS
# ==========================================
class PlatoBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    precio_venta: Decimal = Field(..., gt=0)

class PlatoCreate(PlatoBase):
    recetas: List[RecetaCreate] = Field(default_factory=list)

class PlatoResponse(PlatoBase):
    id: int
    recetas: List[RecetaResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ==========================================
# 4. SCHEMAS PARA COMBOS
# ==========================================
class ComboBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    precio_venta: Decimal = Field(..., gt=0)
    activo: bool = True

class ComboCreate(ComboBase):
    platos_ref: List[Union[int, str]] = Field(
        default_factory=list,
        description="Lista de IDs o Nombres de los platos"
    )

class PlatoBreveResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

class ComboResponse(ComboBase):
    id: int
    # platos: List[PlatoBreveResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True