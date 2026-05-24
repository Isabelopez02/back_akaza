from sqlalchemy.orm import Session
from core.schemas.menu_schema import PlatoCreate, ComboCreate, SustitucionCreate
from infra.repository.menu_repo import MenuRepository

class MenuService:
    """Manages restaurant catalog items, including individual dishes, combo meals, and allowed ingredient swaps."""

    def __init__(self, db: Session):
        self.menu_repo = MenuRepository(db)

    def crear_nuevo_plato(self, data: PlatoCreate):
        """Creates a new catalog dish with corresponding recipe links."""
        try:
            return self.menu_repo.crear_plato(data)
        except Exception as e:
            raise ValueError(f"Error en la lógica al crear el plato: {str(e)}")

    def crear_nuevo_combo(self, data: ComboCreate):
        """Creates a new combo package combining multiple dishes at a bundled price."""
        try:
            return self.menu_repo.crear_combo(data)
        except Exception as e:
            raise ValueError(f"Error en la lógica al crear el combo: {str(e)}")

    def agregar_sustitucion_permitida(self, data: SustitucionCreate):
        """Defines an allowed swap between a base ingredient and a replacement ingredient with dynamic pricing."""
        return self.menu_repo.registrar_sustitucion(data)

    def obtener_carta_para_ia(self) -> dict:
        """
        Retrieves the complete structured restaurant catalog formatted for the chatbot.
        
        Includes individual dishes with ingredients, combos, and registered ingredient swaps.
        """
        platos_db = self.menu_repo.obtener_todos()
        combos_db = self.menu_repo.obtener_todos_los_combos()
        sustituciones_db = self.menu_repo.obtener_todas_las_sustituciones()

        carta_ia = {
            "mensaje_sistema": "Eres un asistente experto. Usa la lista de ingredientes para validar alergias.",
            "platos_individuales": [],
            "combos": [],
            "sustituciones_permitidas": []
        }

        for p in platos_db:
            detalles_ingredientes = []
            if hasattr(p, 'recetas') and p.recetas:
                for r in p.recetas:
                    nombre_prod = r.producto.nombre if hasattr(r, 'producto') else f"ID:{r.id_producto}"
                    detalles_ingredientes.append({
                        "item": nombre_prod,
                        "es_opcional": r.es_opcional,
                        "nota": "Se puede quitar" if r.es_opcional else "Ingrediente base"
                    })

            carta_ia["platos_individuales"].append({
                "id_referencia": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": float(p.precio_venta),
                "imagen_url": p.imagen_url,
                "ingredientes": detalles_ingredientes
            })

        for c in combos_db:
            carta_ia["combos"].append({
                "id_referencia": c.id,
                "nombre": c.nombre,
                "imagen_url": p.imagen_url,
                "precio": float(c.precio_venta)
            })

        for s in sustituciones_db:
            nombre_orig = s.producto_original.nombre if hasattr(s, 'producto_original') and s.producto_original else f"ID:{s.id_producto_original}"
            nombre_nuevo = s.producto_nuevo.nombre if hasattr(s, 'producto_nuevo') and s.producto_nuevo else f"ID:{s.id_producto_nuevo}"

            carta_ia["sustituciones_permitidas"].append({
                "ingrediente_a_quitar": nombre_orig,
                "ingrediente_reemplazo": nombre_nuevo,
                "costo_adicional": float(s.costo_adicional)
            })

        return carta_ia