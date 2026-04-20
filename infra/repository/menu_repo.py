from sqlalchemy.orm import Session
from core.schemas.menu_schema import PlatoCreate
from infra.db.models.menu import Plato

class MenuRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self):
        return self.db.query(Plato).all()

    def obtener_por_id(self, id_plato: int):
        return self.db.query(Plato).filter(Plato.id == id_plato).first()

    def crear_plato(self, data: PlatoCreate):
        nuevo_plato = Plato(
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio_venta=data.precio_venta
        )
        self.db.add(nuevo_plato)
        self.db.commit()
        self.db.refresh(nuevo_plato)
        return nuevo_plato