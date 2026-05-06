from fastapi import Depends

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

# ── Validación de Rol Administrador ──────────────────────────────
def require_admin(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Dependencia que verifica si el usuario autenticado tiene rol de administrador.
    Úsala en los endpoints de /api/admin/ para bloquear accesos no autorizados.
    """
    rol = current_user.get("rol")
    if not rol or rol not in ["administrador", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de administrador."
        )
    return current_user