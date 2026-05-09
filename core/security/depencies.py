from fastapi import Depends, Cookie, HTTPException, status, Request
from core.security.security import decodificar_token

def get_current_user_from_cookie(
    request: Request,
    akaza_token: str | None = Cookie(default=None)
):
    """
    Obtiene el usuario actual desde la cookie 'akaza_token' 
    o desde el header 'Authorization: Bearer <token>'.
    """
    # 1. Intentar obtener token desde Cookie
    token = akaza_token
    
    # 2. Si no hay cookie, intentar desde Header Authorization
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
    
    # 3. Verificar que existe el token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    # 4. Decodificar el token
    try:
        payload = decodificar_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    # 5. Verificar sujeto
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin sujeto",
        )
    
    return payload


def require_admin(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Dependencia que verifica si el usuario autenticado tiene rol de administrador.
    """
    rol = current_user.get("rol")
    
    if not rol or rol not in ["administrador", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de administrador."
        )
    
    return current_user