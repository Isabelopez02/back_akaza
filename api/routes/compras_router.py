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


from datetime import date, datetime
from sqlalchemy import cast, Date

from typing import Optional
@router.get("/", response_model=list[CompraResponse])
def listar_compras_del_dia(fecha: Optional[date] = None, db: Session = Depends(get_db)):
    # Si no envían fecha, tomar la fecha de hoy
    target_date = fecha if fecha else date.today()
    servicio = InventarioService(db)
    
    from infra.db.models.inventario import CompraHistorial
    compras = db.query(CompraHistorial).filter(cast(CompraHistorial.fecha_compra, Date) == target_date).order_by(CompraHistorial.fecha_compra.desc()).all()
    
    # CompraResponse espera 'producto' anidado, así que necesitamos asegurar que la relación exista o cargarla.
    # En infra/db/models/inventario.py no vi relationship de producto en CompraHistorial, pero podemos enriquecer manualmente.
    from infra.db.models.inventario import Producto
    resultado = []
    for c in compras:
        p = db.query(Producto).filter(Producto.id == c.id_producto).first()
        from infra.repository.producto_repo import ProductoRepository
        p_enriquecido = ProductoRepository(db)._enriquecer(p) if p else None
        
        resultado.append(CompraResponse(
            id=c.id,
            id_producto=c.id_producto,
            cantidad_comprada=c.cantidad_comprada,
            unidad_medida=c.unidad_medida,
            precio_unidad_compra=c.precio_unidad_compra,
            fecha_compra=c.fecha_compra,
            producto=p_enriquecido
        ))
    return resultado

@router.post("/", response_model=CompraResponse, status_code=201)
def registrar_compra(data: CompraCreate, db: Session = Depends(get_db)):

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
