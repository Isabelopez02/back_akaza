from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from infra.db.database import get_db
from infra.db.models import Plato 
from core.schemas.menu_schema import PlatoCreate, PlatoUpdate, PlatoResponse
from core.security.depencies import require_admin

router = APIRouter(prefix="/platos", tags=["Admin - Platos"])

# ── LISTAR ──────────────────────────────────────────────────────
@router.get("/", response_model=List[PlatoResponse])
async def listar_platos_admin(db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    """Lista todos los platos (solo admin)"""
    return db.query(Plato).all()

# ── CREAR ──────────────────────────────────────────────────────
@router.post("/", response_model=PlatoResponse, status_code=status.HTTP_201_CREATED)
async def crear_plato_admin(
    plato: PlatoCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Crea un nuevo plato (solo admin)"""
    nuevo_plato = Plato(**plato.model_dump())
    db.add(nuevo_plato)
    db.commit()
    db.refresh(nuevo_plato)
    return nuevo_plato

# ── ACTUALIZAR ─────────────────────────────────────────────────
@router.put("/{plato_id}", response_model=PlatoResponse)
async def actualizar_plato_admin(
    plato_id: int,
    plato_data: PlatoUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Actualiza un plato existente (solo admin)"""
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    for field, value in plato_data.model_dump(exclude_unset=True).items():
        setattr(plato, field, value)
    
    db.commit()
    db.refresh(plato)
    return plato

# ── ELIMINAR ───────────────────────────────────────────────────
@router.delete("/{plato_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_plato_admin(
    plato_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Elimina un plato (solo admin)"""
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    db.delete(plato)
    db.commit()
    return None