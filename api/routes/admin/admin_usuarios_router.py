from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from infra.db.database import get_db
from infra.db.models.usuarios import Usuario, Rol
from core.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from core.security.depencies import require_admin
from core.security.security import encriptar_password

router = APIRouter(prefix="/usuarios", tags=["Admin - Usuarios"])


# ── LISTAR ──────────────────────────────────────────────────────
@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios_admin(
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Lista todos los usuarios (solo admin)"""
  usuarios = db.query(Usuario).all()
  return usuarios


# ── CREAR ──────────────────────────────────────────────────────
@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario_admin(
        usuario: UsuarioCreate,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Crea un nuevo usuario (solo admin)"""
  # Verificar si el correo ya existe
  existe = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
  if existe:
    raise HTTPException(status_code=400, detail="El correo ya está registrado.")

  # Obtener rol por defecto (ej. Cliente o Cajero, aquí asumo el rol básico si no se envía, o si id_rol fuera requerido)
  # Buscamos el rol 'Mesero' o 'Cliente'
  rol = db.query(Rol).filter(Rol.nombre == "Mesero").first()
  if not rol:
    rol = db.query(Rol).first()

  # Crear usuario
  hashed_password = encriptar_password(usuario.contrasenia)
  nuevo_usuario = Usuario(
    nombre=usuario.nombre,
    correo=usuario.correo,
    contrasenia=hashed_password,
    id_rol=rol.id if rol else 1
  )

  db.add(nuevo_usuario)
  db.commit()
  db.refresh(nuevo_usuario)
  return nuevo_usuario


# ── ELIMINAR ───────────────────────────────────────────────────
@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario_admin(
        usuario_id: int,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Elimina un usuario (solo admin)"""
  usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
  if not usuario:
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

  # En un sistema real podría ser borrado lógico o eliminar el perfil primero.
  # Aquí hacemos un borrado físico simple:
  db.delete(usuario)
  db.commit()
  return None
