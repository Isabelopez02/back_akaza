from sqlalchemy.orm import Session

class IAService:
    """
    Orquestador principal de Leia
    Combina IA (Gemini) + lógica del negocio
    """

    def __init__(self, db: Session):
        self.db = db

    # =========================
    # 💬 RESPUESTA GENERAL
    # =========================
    def procesar(self, input_ia: dict, id_usuario: int = 1, nro_mesa: int = 1):

        intencion = input_ia.get("intencion")
        mensaje_ia = input_ia.get("mensaje", "")

        # 🟢 SALUDO / INFO → usar mensaje directo de Gemini
        if intencion in ["saludo", "info_restaurante", "desconocida"]:
            return {
                "mensaje": mensaje_ia
            }

        # =========================
        # 🍽️ RECOMENDACIONES
        # =========================
        if intencion == "recomendacion":
            contexto = input_ia.get("contexto", {})

            # 🔥 luego aquí conectas a RecomendacionService real
            if contexto.get("estado") == "resfriado":
                return {
                    "mensaje": mensaje_ia + " Además, te recomiendo algo caliente como un caldo de pescado 🍲",
                    "data": []
                }

            return {
                "mensaje": mensaje_ia + " Te sugiero ceviche o arroz con mariscos 🐟",
                "data": []
            }

        # =========================
        # 🧾 PEDIDOS
        # =========================
        if intencion == "pedido":
            articulos = input_ia.get("articulos", [])

            if not articulos:
                return {
                    "mensaje": "Aún no tengo claro tu pedido 😅 ¿qué plato deseas?"
                }

            # 🔥 aquí luego llamas a PedidoService real
            return {
                "mensaje": "Perfecto 😊 tu pedido fue enviado a cocina 🍽️",
                "data": articulos
            }

        return {
            "mensaje": "No entendí muy bien 😅 ¿puedes repetirlo?"
        }