from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ==========================================
# 1. SCHEMAS PARA ROL
# ==========================================
class RolBase(BaseModel):
  nombre: str = Field(..., min_length=3, max_length=50)


class RolCreate(RolBase):
  pass


class RolResponse(RolBase):
  id: int

  class Config:
    from_attributes = True


# ==========================================
# 2. SCHEMAS PARA PERFIL USUARIO
# ==========================================
class PerfilUsuarioBase(BaseModel):
  es_temporal: bool = False
  id_mesa_actual: Optional[int] = None
  alergias: Optional[str] = None
  preferencias: Optional[str] = None
  observaciones_ia: Optional[str] = None


class PerfilUsuarioCreate(PerfilUsuarioBase):
  # AQUÍ ESTÁ TU LÓGICA: Pedimos el nombre en texto, no el ID.
  # Le ponemos "CLIENTE" por defecto para que ni siquiera sea obligatorio enviarlo.
  nombre_rol: str = Field(default="CLIENTE", description="Nombre del rol a buscar en la BD")


class PerfilUsuarioResponse(PerfilUsuarioBase):
  id_usuario: int
  id_rol: int

  # rol: Optional[RolResponse] = None # (Opcional si quieres que también devuelva el nombre del rol al consultar)

  class Config:
    from_attributes = True


# ==========================================
# 3. SCHEMAS PARA USUARIO PRINCIPAL
# ==========================================
class UsuarioBase(BaseModel):
  nombre: str = Field(... , min_length=2, max_length=50)
  correo: EmailStr  # Valida automáticamente que tenga el @ y un dominio


class UsuarioCreate(UsuarioBase):
  contrasenia: str = Field(... , min_length= 6)
  # Permitimos crear el usuario y su perfil de un solo golpe desde Postman/Frontend
  perfil: Optional[PerfilUsuarioCreate] = None


class UsuarioResponse(UsuarioBase):
  id: int
  creado_en: datetime
  # Lo ponemos Optional porque al crearlo recién, modificado_en será nulo
  modificado_en: Optional[datetime] = None

  perfil: Optional[PerfilUsuarioResponse] = None

  class Config:
    from_attributes = True