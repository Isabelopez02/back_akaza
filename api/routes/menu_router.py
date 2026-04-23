from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.schemas.menu_schema import PlatoCreate, ComboCreate, SustitucionCreate
# Asegúrate de importar tu get_db y tu MenuService desde las rutas correctas
from infra.db.database import get_db
from core.services.menu_service import MenuService

router = APIRouter(prefix="/api/menu", tags=["Menú y Carta"])

@router.post("/platos")
def crear_plato(data: PlatoCreate, db: Session = Depends(get_db)):
    servicio = MenuService(db)
    return servicio.crear_nuevo_plato(data)

@router.post("/combos")
def crear_combo(data: ComboCreate, db: Session = Depends(get_db)):
    servicio = MenuService(db)
    return servicio.crear_nuevo_combo(data)

@router.post("/sustituciones")
def registrar_sustitucion(data: SustitucionCreate, db: Session = Depends(get_db)):
    servicio = MenuService(db)
    return servicio.agregar_sustitucion_permitida(data)

# 🔥 EL ENDPOINT PARA TU IA
@router.get("/ia/carta-completa")
def obtener_carta_ia(db: Session = Depends(get_db)):
    servicio = MenuService(db)
    return servicio.obtener_carta_para_ia()