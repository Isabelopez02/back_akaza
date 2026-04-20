from fastapi import APIRouter
from pydantic import BaseModel
from core.services.chatbot import responder_chat

#Creación del router para las rutas del chatbot
router = APIRouter()

class Mensaje(BaseModel):
    mensaje: str

# Endpoint para recibir mensajes del chatbot y responder
@router.post("/chat")
def chat_api(data: Mensaje):
    respuesta = responder_chat(data.mensaje)
    return {"respuesta": respuesta}

# ==========================================
# NUEVOS ENDPOINTS
# ==========================================
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from infra.db.database import get_db
from infra.repository.producto_repo import ProductoRepository
from infra.repository.menu_repo import MenuRepository
from core.schemas.inventario_schema import ProductoCreate, ProductoResponse
from core.schemas.menu_schema import PlatoCreate, PlatoResponse

# ==========================================
# ENDPOINTS PARA PRODUCTOS (Inventario)
# ==========================================
@router.post("/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    """Registra un nuevo insumo en el inventario."""
    repo = ProductoRepository(db)
    return repo.crear_producto(data)

@router.get("/productos", response_model=List[ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    """Obtiene la lista completa de productos/insumos."""
    repo = ProductoRepository(db)
    return repo.obtener_todos()

@router.get("/productos/{id_producto}", response_model=ProductoResponse)
def obtener_producto(id_producto: int, db: Session = Depends(get_db)):
    """Busca un producto específico por su ID."""
    repo = ProductoRepository(db)
    producto = repo.obtener_por_id(id_producto)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


# ==========================================
# ENDPOINTS PARA MENÚ (Platos)
# ==========================================
@router.post("/menu/platos", response_model=PlatoResponse, status_code=status.HTTP_201_CREATED)
def crear_plato(data: PlatoCreate, db: Session = Depends(get_db)):
    """Agrega un nuevo plato al menú del restaurante."""
    repo = MenuRepository(db)
    return repo.crear_plato(data)

@router.get("/menu/platos", response_model=List[PlatoResponse])
def listar_platos(db: Session = Depends(get_db)):
    """Obtiene todos los platos disponibles en el menú."""
    repo = MenuRepository(db)
    return repo.obtener_todos()

@router.get("/menu/platos/{id_plato}", response_model=PlatoResponse)
def obtener_plato(id_plato: int, db: Session = Depends(get_db)):
    """Busca un plato específico por su ID."""
    repo = MenuRepository(db)
    plato = repo.obtener_por_id(id_plato)
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    return plato

# ==========================================
# ACTUALIZAR Y ELIMINAR (Completar CRUD)
# ==========================================
@router.put("/productos/{id_producto}", response_model=ProductoResponse)
def actualizar_producto(id_producto: int, data: ProductoCreate, db: Session = Depends(get_db)):
    """Actualiza todos los datos de un producto."""
    repo = ProductoRepository(db)
    resultado = repo.actualizar_producto(id_producto, data)
    if not resultado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return resultado

@router.delete("/productos/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(id_producto: int, db: Session = Depends(get_db)):
    """Elimina un producto del inventario."""
    repo = ProductoRepository(db)
    repo.eliminar_producto(id_producto)
    # 204 significa "Éxito, pero no devuelvo datos" (estándar para DELETE)

# ==========================================
# ENDPOINTS PARA PEDIDOS (Ventas)
# ==========================================
from infra.repository.pedido_repo import PedidoRepository
from core.schemas.venta_schema import PedidoCreate, PedidoResponse
@router.post("/pedidos", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(data: PedidoCreate, db: Session = Depends(get_db)):
    """Registra un nuevo pedido en una mesa."""
    repo = PedidoRepository(db)
    return repo.crear_pedido(data)

@router.get("/pedidos/{id_pedido}", response_model=PedidoResponse)
def obtener_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """Consulta un pedido específico por su ID."""
    repo = PedidoRepository(db)
    pedido = repo.obtener_pedido_por_id(id_pedido)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido

@router.get("/mesas/{nro_mesa}/pedidos", response_model=list[PedidoResponse])
def pedidos_por_mesa(nro_mesa: int, db: Session = Depends(get_db)):
    """Lista todos los pedidos activos de una mesa."""
    repo = PedidoRepository(db)
    return repo.listar_pedidos_por_mesa(nro_mesa)