from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.schemas.venta_schema import PedidoCreate
from infra.db.database import get_db
from core.services.pedido_service import PedidoService

router = APIRouter(prefix="/api/pedidos", tags=["Gestión de Pedidos"])

# 🔥 EL ENDPOINT DONDE LA IA MANDA EL PEDIDO EN BORRADOR
@router.post("/")
def registrar_pedido_ia(data: PedidoCreate, db: Session = Depends(get_db)):
    servicio = PedidoService(db)
    try:
        return servicio.registrar_nuevo_pedido(data)
    except ValueError as e:
        # Si salta la regla de los 5 minutos, mandamos un error 409 (Conflicto)
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/mesa/{nro_mesa}")
def ver_pedidos_mesa(nro_mesa: int, db: Session = Depends(get_db)):
    servicio = PedidoService(db)
    return servicio.listar_pedidos_mesa(nro_mesa)

from typing import List
from core.schemas.venta_schema import PedidoResponse

@router.get("/", response_model=List[PedidoResponse])
def listar_todos_pedidos(db: Session = Depends(get_db)):
    servicio = PedidoService(db)
    return servicio.listar_todos_pedidos()

# 🔥 EL ENDPOINT CUANDO EL CLIENTE DICE "SÍ, ESTOY DE ACUERDO"
@router.put("/{id_pedido}/confirmar")
def confirmar_pedido_cocina(id_pedido: int, db: Session = Depends(get_db)):
    servicio = PedidoService(db)
    return servicio.confirmar_pedido_ia(id_pedido)

@router.put("/{id_pedido}/pagar")
def pagar_pedido(id_pedido: int, metodo_pago: str = "EFECTIVO", 
                 monto_efectivo: float = 0.0, monto_yape: float = 0.0, monto_tarjeta: float = 0.0,
                 db: Session = Depends(get_db)):
    servicio = PedidoService(db)
    try:
        return servicio.pagar_pedido(
            id_pedido, 
            metodo_pago=metodo_pago,
            monto_efectivo=monto_efectivo,
            monto_yape=monto_yape,
            monto_tarjeta=monto_tarjeta
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id_pedido}/anular")
def anular_pedido(id_pedido: int, db: Session = Depends(get_db)):
    servicio = PedidoService(db)
    return servicio.cancelar_o_anular_pedido(id_pedido)