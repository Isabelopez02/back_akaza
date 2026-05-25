from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from infra.db.database import get_db
from infra.db.models.usuarios import Usuario, Rol
from core.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioResponse, RolResponse
from core.security.depencies import require_admin
from core.security.security import encriptar_password

router = APIRouter(prefix="/usuarios", tags=["Admin - Usuarios"])

@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios_admin(
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Lista todos los usuarios registrados (solo para administradores)."""
  return db.query(Usuario).all()


@router.get("/roles", response_model=List[RolResponse])
async def listar_roles_admin(
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Lista todos los roles del sistema disponibles (solo para administradores)."""
  return db.query(Rol).all()


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario_admin(
        usuario: UsuarioCreate,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Registra un nuevo usuario en el sistema con credenciales encriptadas (solo para administradores)."""
  # Verificar si el correo ya está registrado
  existe = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
  if existe:
    raise HTTPException(status_code=400, detail="El correo ya está registrado.")

  # Asignar rol
  if usuario.id_rol:
    rol = db.query(Rol).filter(Rol.id == usuario.id_rol).first()
    if not rol:
      raise HTTPException(status_code=400, detail="El rol especificado no existe.")
  else:
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


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario_admin(
        usuario_id: int,
        usuario_update: UsuarioUpdate,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Actualiza las credenciales o el rol de un usuario existente (solo para administradores)."""
  usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
  if not usuario:
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

  # Impedir que se editen usuarios con rol de administrador
  if usuario.rol and usuario.rol.nombre.lower() in ["administrador", "admin"]:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Acceso denegado. Los usuarios con rol de administrador están protegidos y no pueden ser editados."
    )

  if usuario_update.correo and usuario_update.correo != usuario.correo:
    existe = db.query(Usuario).filter(Usuario.correo == usuario_update.correo).first()
    if existe:
      raise HTTPException(status_code=400, detail="El correo ya está registrado por otro usuario.")
    usuario.correo = usuario_update.correo

  if usuario_update.nombre is not None:
    usuario.nombre = usuario_update.nombre

  if usuario_update.id_rol is not None:
    rol = db.query(Rol).filter(Rol.id == usuario_update.id_rol).first()
    if not rol:
      raise HTTPException(status_code=400, detail="El rol especificado no existe.")
    usuario.id_rol = usuario_update.id_rol

  if usuario_update.contrasenia is not None:
    usuario.contrasenia = encriptar_password(usuario_update.contrasenia)

  db.commit()
  db.refresh(usuario)
  return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario_admin(
        usuario_id: int,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Elimina la cuenta de un usuario específico (solo para administradores)."""
  usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
  if not usuario:
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

  # Impedir que se eliminen usuarios con rol de administrador
  if usuario.rol and usuario.rol.nombre.lower() in ["administrador", "admin"]:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Acceso denegado. Los usuarios con rol de administrador están protegidos y no pueden ser eliminados."
    )

  db.delete(usuario)
  db.commit()
  return None
