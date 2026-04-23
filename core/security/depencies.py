from fastapi import Cookie, HTTPException, status

from core.security.security import decodificar_token


def get_current_user_from_cookie(akaza_token: str | None = Cookie(default=None)):
    if not akaza_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    payload = decodificar_token(akaza_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin sujeto (sub)",
        )
    return payload
