"""
Router de Compras — POST /api/compras
Registra el ingreso de mercadería: suma stock, rota precio y guarda historial.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.schemas.inventario_schema import CompraCreate, CompraResponse
from infra.db.database import get_db
from core.services.inventario_service import InventarioService

router = APIRouter(prefix="/api/compras", tags=["Módulo de Compras"])


@router.post("/", response_model=CompraResponse, status_code=201)
def registrar_compra(data: CompraCreate, db: Session = Depends(get_db)):
    """
    Registra una compra de mercadería.

    - Suma `cantidad` al `stock_actual` del producto.
    - Guarda `precio_unitario` como nuevo `precio_compra` del producto.
    - El precio anterior queda en `precio_compra_anterior` para comparación visual.
    - Inserta un registro en `compras_historial`.

    **Body esperado:**
    ```json
    {
      "id_producto": 3,
      "cantidad": 5,
      "unidad_medida": "kg",
      "precio_unitario": 12.50
    }
    ```
    """
    servicio = InventarioService(db)
    try:
        registro, producto = servicio.registrar_compra(data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return CompraResponse(
        id=registro.id,
        id_producto=registro.id_producto,
        cantidad_comprada=registro.cantidad_comprada,
        unidad_medida=registro.unidad_medida,
        precio_unidad_compra=registro.precio_unidad_compra,
        fecha_compra=registro.fecha_compra,
        producto=producto,
    )
