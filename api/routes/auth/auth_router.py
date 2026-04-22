from fastapi import APIRouter, Response, HTTPException, Depends, status
from sqlalchemy.orm import Session
from core.security.security import crear_token_jwt
from core.security.depencies import get_current_user_from_cookie
from core.schemas.usuario_schema import LoginRequest, UsuarioCreate
from infra.db.database import get_db
from infra.repository.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/register")
def register_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
  repo = UsuarioRepository(db)
  try:
    usuario = repo.crear_usuario(data)
    return {"id": usuario.id, "correo": usuario.correo}
  except ValueError as e:
    raise HTTPException(status_code=409, detail=str(e))


@router.post("/login")
def login_usuario(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
  repo = UsuarioRepository(db)
  usuario = repo.validar_credenciales(payload.correo, payload.contrasenia)

  if not usuario:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Credenciales incorrectas",
    )

  token = crear_token_jwt({"sub": str(usuario.id), "correo": usuario.correo})

  response.set_cookie(
    key="akaza_token",
    value=token,
    httponly=True,
    secure=False,
    samesite="lax",
    max_age=60 * 60 * 3,
    path="/",
  )

  return {"mensaje": "Login exitoso"}


@router.get("/me")
def obtener_usuario_actual(payload: dict = Depends(get_current_user_from_cookie)):
  return {
    "id_usuario": payload.get("sub"),
    "correo": payload.get("correo"),
    "autenticado": True,
  }