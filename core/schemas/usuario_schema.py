import re
from pydantic import BaseModel, EmailStr, Field, field_validator
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
  pass


class PerfilUsuarioResponse(PerfilUsuarioBase):
  id_usuario: int

  class Config:
    from_attributes = True


# ==========================================
# 3. SCHEMAS PARA USUARIO PRINCIPAL
# ==========================================
class UsuarioBase(BaseModel):
  nombre: str = Field(... , min_length=2, max_length=50)
  correo: EmailStr


class UsuarioCreate(UsuarioBase):
  contrasenia: str = Field(..., min_length=8, max_length=72)
  id_rol: Optional[int] = None

  @field_validator("contrasenia")
  @classmethod
  def validar_password_segura(cls, v: str) -> str:
    if not re.search(r"[A-Z]", v):
      raise ValueError("Debe incluir al menos una mayúscula.")
    if not re.search(r"[a-z]", v):
      raise ValueError("Debe incluir al menos una minúscula.")
    if not re.search(r"\d", v):
      raise ValueError("Debe incluir al menos un número.")
    if not re.search(r"[^\w\s]", v):
      raise ValueError("Debe incluir al menos un carácter especial.")
    return v


class UsuarioUpdate(BaseModel):
  nombre: Optional[str] = Field(None, min_length=2, max_length=50)
  correo: Optional[EmailStr] = None
  contrasenia: Optional[str] = Field(None, min_length=8, max_length=72)
  id_rol: Optional[int] = None

  @field_validator("contrasenia")
  @classmethod
  def validar_password_segura(cls, v: Optional[str]) -> Optional[str]:
    if v is None:
      return v
    if not re.search(r"[A-Z]", v):
      raise ValueError("Debe incluir al menos una mayúscula.")
    if not re.search(r"[a-z]", v):
      raise ValueError("Debe incluir al menos una minúscula.")
    if not re.search(r"\d", v):
      raise ValueError("Debe incluir al menos un número.")
    if not re.search(r"[^\w\s]", v):
      raise ValueError("Debe incluir al menos un carácter especial.")
    return v


class LoginRequest(BaseModel):
  correo: EmailStr
  contrasenia: str = Field(..., min_length=1)


class UsuarioResponse(UsuarioBase):
  id: int
  id_rol: int
  creado_en: datetime
  modificado_en: Optional[datetime] = None
  perfil: Optional[PerfilUsuarioResponse] = None
  rol: Optional[RolResponse] = None

  class Config:
    from_attributes = True

# ==========================================
# 4. MODELO UNIFICADO (CUENTA COMPLETA)
# ==========================================
class UnifiedUserAccount(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    alergias: Optional[str] = ""
    preferencias: Optional[str] = ""
    id_mesa_actual: Optional[int] = None
    autenticado: bool = True

    class Config:
        from_attributes = True