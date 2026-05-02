from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.schemas.inventario_schema import ProductoCreate, ProductoResponse
from infra.db.database import get_db
from core.services.inventario_service import InventarioService

router = APIRouter(prefix="/api/inventario", tags=["Inventario y Alertas"])


@router.get("/", response_model=List[ProductoResponse])
def listar_todos_productos(db: Session = Depends(get_db)):
    return InventarioService(db).listar_productos()


@router.post("/", response_model=ProductoResponse, status_code=201)
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    return InventarioService(db).registrar_producto(data)


@router.get("/alertas")
def ver_alertas_stock(db: Session = Depends(get_db)):
    return InventarioService(db).obtener_alertas_stock()


@router.put("/{id_producto}/mover-stock", response_model=ProductoResponse)
def ajustar_stock(id_producto: int, cantidad: float, db: Session = Depends(get_db)):
    try:
        return InventarioService(db).mover_stock(id_producto, cantidad)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id_producto}", status_code=200)
def eliminar_producto(id_producto: int, db: Session = Depends(get_db)):
    try:
        return InventarioService(db).borrar_producto(id_producto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))