import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no está configurada en el entorno.")

ALGORITHM = "HS256"
MINUTOS_EXPIRACION = 180

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encriptar_password(password: str) -> str:
    return pwd_context.hash(password)


def verificar_password(password_plana: str, password_encriptada: str) -> bool:
    return pwd_context.verify(password_plana, password_encriptada)


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