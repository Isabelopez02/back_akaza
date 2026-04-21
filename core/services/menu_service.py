from sqlalchemy.orm import Session
from core.schemas.menu_schema import PlatoCreate, ComboCreate, SustitucionCreate
from infra.repository.menu_repo import MenuRepository

class MenuService:
    def __init__(self, db: Session):
        self.menu_repo = MenuRepository(db)

    # ==========================================
    # 1. MÉTODOS DE CREACIÓN (Para el Administrador)
    # ==========================================
    def crear_nuevo_plato(self, data: PlatoCreate):
        try:
            return self.menu_repo.crear_plato(data)
        except Exception as e:
            raise ValueError(f"Error en la lógica al crear el plato: {str(e)}")

    def crear_nuevo_combo(self, data: ComboCreate):
        try:
            return self.menu_repo.crear_combo(data)
        except Exception as e:
            raise ValueError(f"Error en la lógica al crear el combo: {str(e)}")

    def agregar_sustitucion_permitida(self, data: SustitucionCreate):
        return self.menu_repo.registrar_sustitucion(data)

    # ==========================================
    # 2. MÉTODO ESTRELLA (Para tu IA)
    # ==========================================
    def obtener_carta_para_ia(self) -> dict:
        """
        Este método es clave. Llama al repositorio, obtiene todos los platos
        y combos activos, y los formatea en un diccionario (JSON).
        Esto es lo que le vas a pasar a tu IA en 'contexto_enviado'.
        """
        platos_db = self.menu_repo.obtener_todos()
        combos_db = self.menu_repo.obtener_todos_los_combos()

        carta_ia = {
            "mensaje_sistema": "Esta es la carta disponible hoy en el restaurante de comida marina.",
            "platos_individuales": [],
            "combos": []
        }

        # Formateamos los platos
        for p in platos_db:
            carta_ia["platos_individuales"].append({
                "id_referencia": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": float(p.precio_venta)
            })

        # Formateamos los combos
        for c in combos_db:
            carta_ia["combos"].append({
                "id_referencia": c.id,
                "nombre": c.nombre,
                "precio": float(c.precio_venta)
            })

        return carta_ia