import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException, status

import hashlib
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no está configurada en el entorno.")

ALGORITHM = "HS256"
MINUTOS_EXPIRACION = 180


def _normalizar_password_bcrypt(password: str) -> bytes:
    """
    bcrypt trabaja con un límite de 72 bytes.
    Si entra una clave más larga, la recortamos de forma segura.
    """
    return password.encode("utf-8")[:72]


def encriptar_password(password: str) -> str:
    password_normalizada = _normalizar_password_bcrypt(password)
    password_bytes = hashlib.sha256(password_normalizada).digest()
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verificar_password(password_plana: str, password_encriptada: str) -> bool:
    password_normalizada = _normalizar_password_bcrypt(password_plana)
    password_bytes = hashlib.sha256(password_normalizada).digest()
    return bcrypt.checkpw(password_bytes, password_encriptada.encode("utf-8"))

def crear_token_jwt(data: dict, minutos_exp: int = MINUTOS_EXPIRACION) -> str:
    ahora = datetime.now(timezone.utc)
    payload = data.copy()
    payload.update(
        {
            "iat": ahora,
            "exp": ahora + timedelta(minutes=minutos_exp),
            "type": "access",
        }
    )
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )