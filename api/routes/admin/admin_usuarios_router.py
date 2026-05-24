from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from infra.db.database import get_db
from infra.db.models.usuarios import Usuario, Rol
from core.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from core.security.depencies import require_admin
from core.security.security import encriptar_password

router = APIRouter(prefix="/usuarios", tags=["Admin - Usuarios"])

@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios_admin(
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Lists all registered users (admin-only)."""
  return db.query(Usuario).all()


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario_admin(
        usuario: UsuarioCreate,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Registers a new system user with hashed credentials (admin-only)."""
  # Verify if email is already registered
  existe = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
  if existe:
    raise HTTPException(status_code=400, detail="El correo ya está registrado.")

  # Retrieve basic role fallback
  rol = db.query(Rol).filter(Rol.nombre == "Mesero").first()
  if not rol:
    rol = db.query(Rol).first()

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


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario_admin(
        usuario_id: int,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Deletes a specific user account (admin-only)."""
  usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
  if not usuario:
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

  db.delete(usuario)
  db.commit()
  return None
