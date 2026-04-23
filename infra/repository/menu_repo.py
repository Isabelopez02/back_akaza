from sqlalchemy.orm import Session
# Asegúrate de importar el modelo Producto para poder buscar por nombre
from infra.db.models.inventario import Producto
# IMPORTANTE: Agregamos ComboPlato aquí
from infra.db.models.menu import Plato, Receta, SustitucionPermitida, Combo, ComboPlato
from core.schemas.menu_schema import PlatoCreate, RecetaCreate, SustitucionCreate, ComboCreate

class MenuRepository:
    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # FUNCIONES AUXILIARES: La magia para entender a la IA
    # =========================================================
    def _resolver_id_producto(self, referencia: int | str) -> int:
        """Busca ingredientes por ID o Nombre."""
        if isinstance(referencia, int) or (isinstance(referencia, str) and referencia.isdigit()):
            return int(referencia)
        producto_db = self.db.query(Producto).filter(Producto.nombre.ilike(f"%{referencia}%")).first()
        if not producto_db:
            raise ValueError(f"El producto '{referencia}' no existe en la base de datos.")
        return producto_db.id

    def _resolver_id_plato(self, referencia: int | str) -> int:
        """Busca platos por ID o Nombre."""
        if isinstance(referencia, int) or (isinstance(referencia, str) and referencia.isdigit()):
            return int(referencia)
        plato_db = self.db.query(Plato).filter(Plato.nombre.ilike(f"%{referencia}%")).first()
        if not plato_db:
            raise ValueError(f"El plato '{referencia}' no existe en el menú.")
        return plato_db.id

    # =========================================================
    # LÓGICA DE PLATOS Y RECETAS
    # =========================================================
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

        if hasattr(data, 'recetas') and data.recetas:
            for receta_data in data.recetas:
                self.crear_receta(nuevo_plato.id, receta_data)

        return nuevo_plato

    def crear_receta(self, id_plato: int, data: RecetaCreate):
        id_producto_real = self._resolver_id_producto(data.producto_ref)
        nueva_receta = Receta(
            id_plato=id_plato,
            id_producto=id_producto_real,
            cantidad_estimada=data.cantidad_estimada,
            unidad_medida=data.unidad_medida,
            es_opcional=data.es_opcional
        )
        self.db.add(nueva_receta)
        self.db.commit()
        self.db.refresh(nueva_receta)
        return nueva_receta

    def registrar_sustitucion(self, data: SustitucionCreate):
        id_orig = self._resolver_id_producto(data.producto_original_ref)
        id_nuevo = self._resolver_id_producto(data.producto_nuevo_ref)
        nueva_sustitucion = SustitucionPermitida(
            id_producto_original=id_orig,
            id_producto_nuevo=id_nuevo,
            costo_adicional=data.costo_adicional
        )
        self.db.add(nueva_sustitucion)
        self.db.commit()
        self.db.refresh(nueva_sustitucion)
        return nueva_sustitucion

    def obtener_receta_por_plato(self, id_plato: int):
        return self.db.query(Receta).filter(Receta.id_plato == id_plato).all()

    # =========================================================
    # LÓGICA DE COMBOS (Ahora sí dentro de la clase)
    # =========================================================
    def crear_combo(self, data: ComboCreate):
        try:
            nuevo_combo = Combo(
                nombre=data.nombre,
                precio_venta=data.precio_venta,
                activo=data.activo
            )
            self.db.add(nuevo_combo)
            self.db.flush()

            for plato_ref in data.platos_ref:
                id_plato_real = self._resolver_id_plato(plato_ref)
                detalle_combo = ComboPlato(
                    id_combo=nuevo_combo.id,
                    id_plato=id_plato_real
                )
                self.db.add(detalle_combo)

            self.db.commit()
            self.db.refresh(nuevo_combo)
            return nuevo_combo

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al crear el combo: {str(e)}")

    def obtener_todos_los_combos(self):
        return self.db.query(Combo).filter(Combo.activo == True).all()

    def obtener_todas_las_sustituciones(self):
        return self.db.query(SustitucionPermitida).all()