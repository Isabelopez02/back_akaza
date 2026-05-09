from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from infra.db.database import get_db
from infra.db.models.menu import Combo, ComboPlato
from core.schemas.menu_schema import ComboCreate, ComboUpdate, ComboResponse
from core.security.depencies import require_admin
from infra.repository.menu_repo import MenuRepository

router = APIRouter(prefix="/combos", tags=["Admin - Combos"])


# ── LISTAR ──────────────────────────────────────────────────────
@router.get("/", response_model=List[ComboResponse])
async def listar_combos_admin(
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Lista todos los combos (solo admin)"""
  combos = db.query(Combo).filter(Combo.activo == True).all()
  return combos


# ── CREAR ──────────────────────────────────────────────────────
@router.post("/", response_model=ComboResponse, status_code=status.HTTP_201_CREATED)
async def crear_combo_admin(
        combo: ComboCreate,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Crea un nuevo combo (solo admin)"""
  repo = MenuRepository(db)
  try:
    nuevo_combo = repo.crear_combo(combo)
    return nuevo_combo
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))


# ── ACTUALIZAR ─────────────────────────────────────────────────
@router.put("/{combo_id}", response_model=ComboResponse)
async def actualizar_combo_admin(
        combo_id: int,
        combo_data: ComboUpdate,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Actualiza un combo existente (solo admin)"""
  combo = db.query(Combo).filter(Combo.id == combo_id).first()
  if not combo:
    raise HTTPException(status_code=404, detail="Combo no encontrado")

  update_data = combo_data.model_dump(exclude_unset=True)

  if "platos_ref" in update_data:
    platos_ref = update_data.pop("platos_ref")
    # Eliminar platos antiguos
    db.query(ComboPlato).filter(ComboPlato.id_combo == combo.id).delete()
    db.commit()
    # Agregar nuevos platos
    repo = MenuRepository(db)
    if platos_ref:
      for plato_ref in platos_ref:
        id_plato_real = repo._resolver_id_plato(plato_ref)
        detalle_combo = ComboPlato(
          id_combo=combo.id,
          id_plato=id_plato_real
        )
        db.add(detalle_combo)

  for field, value in update_data.items():
    setattr(combo, field, value)

  db.commit()
  db.refresh(combo)
  return combo


# ── ELIMINAR ───────────────────────────────────────────────────
@router.delete("/{combo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_combo_admin(
        combo_id: int,
        db: Session = Depends(get_db),
        admin: dict = Depends(require_admin)
):
  """Elimina un combo lógicamente (solo admin)"""
  combo = db.query(Combo).filter(Combo.id == combo_id).first()
  if not combo:
    raise HTTPException(status_code=404, detail="Combo no encontrado")

  combo.activo = False
  db.commit()
  return None
