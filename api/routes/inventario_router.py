from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.schemas.inventario_schema import ProductoCreate
from infra.db.database import get_db
from core.services.inventario_service import InventarioService

router = APIRouter(prefix="/api/inventario", tags=["Inventario y Alertas"])

@router.get("/")
def listar_todos_productos(db: Session = Depends(get_db)):
    servicio = InventarioService(db)
    return servicio.listar_productos()

@router.post("/")
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    servicio = InventarioService(db)
    return servicio.registrar_producto(data)

# 🔥 EL ENDPOINT PARA EL DASHBOARD DE ALERTAS
@router.get("/alertas")
def ver_alertas_stock(db: Session = Depends(get_db)):
    servicio = InventarioService(db)
    return servicio.obtener_alertas_stock()

@router.put("/{id_producto}/mover-stock")
def ajustar_stock(id_producto: int, cantidad: float, db: Session = Depends(get_db)):
    servicio = InventarioService(db)
    try:
        return servicio.mover_stock(id_producto, cantidad)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))