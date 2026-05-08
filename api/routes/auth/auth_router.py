import jwt
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.security.security import crear_token_jwt, decodificar_token, SECRET_KEY, ALGORITHM
from core.schemas.usuario_schema import LoginRequest, UsuarioCreate
from infra.db.database import get_db
from infra.repository.usuario_repo import UsuarioRepository
from infra.db.models.usuarios import Usuario

security = HTTPBearer()

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
def login_usuario(payload: LoginRequest, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    usuario = repo.validar_credenciales(payload.correo, payload.contrasenia)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    token = crear_token_jwt({
        "sub": str(usuario.id),
        "correo": usuario.correo,
        "rol": usuario.rol.nombre if usuario.rol else "cliente", 
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "nombre": usuario.nombre,
        "rol": usuario.rol.nombre if usuario.rol else "cliente"
    }


@router.get("/me")
def obtener_usuario_actual(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decodificar_token(token)
        user_id = payload.get("sub")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = UsuarioRepository(db)
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol.nombre if usuario.rol else "cliente",
        "autenticado": True,
    }