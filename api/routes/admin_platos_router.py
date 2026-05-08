from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from infra.db.database import get_db
from infra.db.models.menu import Plato, Receta
from core.schemas.menu_schema import PlatoCreate, PlatoUpdate, PlatoResponse
from core.security.depencies import require_admin
from infra.repository.menu_repo import MenuRepository

router = APIRouter(prefix="/platos", tags=["Admin - Platos"])

# ── LISTAR ──────────────────────────────────────────────────────
@router.get("/", response_model=List[PlatoResponse])
async def listar_platos_admin(
    db: Session = Depends(get_db), 
    admin: dict = Depends(require_admin)  # ✅ SEGURIDAD ACTIVADA
):
    """Lista todos los platos (solo admin)"""
    platos = db.query(Plato).all()
    return platos

# ── CREAR ──────────────────────────────────────────────────────
@router.post("/", response_model=PlatoResponse, status_code=status.HTTP_201_CREATED)
async def crear_plato_admin(
    plato: PlatoCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Crea un nuevo plato (solo admin)"""
    repo = MenuRepository(db)
    try:
        nuevo_plato = repo.crear_plato(plato)
        return nuevo_plato
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    
    update_data = plato_data.model_dump(exclude_unset=True)
    
    if "recetas" in update_data:
        recetas_data = update_data.pop("recetas")
        # Eliminar recetas antiguas
        db.query(Receta).filter(Receta.id_plato == plato.id).delete()
        db.commit()
        # Agregar nuevas recetas
        repo = MenuRepository(db)
        if recetas_data:
            for r_data in plato_data.recetas:
                repo.crear_receta(plato.id, r_data)
    
    for field, value in update_data.items():
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
    
    # Eliminar recetas relacionadas primero
    db.query(Receta).filter(Receta.id_plato == plato.id).delete()
    
    db.delete(plato)
    db.commit()
    return None