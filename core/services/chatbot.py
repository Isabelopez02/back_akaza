import os
import json
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
from dotenv import load_dotenv

from core.services.menu_service import MenuService
from infra.repository.chat_repo import ChatRepository

load_dotenv()


class ChatService:
  def __init__(self, db: Session):
    self.db = db
    self.menu_service = MenuService(db)
    self.chat_repo = ChatRepository(db)  # ¡Inyectamos tu nuevo repositorio!
    self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    self.modelo = "gemini-3-flash-preview"

  def procesar_mensaje(self, id_usuario: int, nro_mesa: int, mensaje: str) -> str:
    try:
      # 1. Obtenemos el contexto (La carta actual)
      carta_actual = self.menu_service.obtener_carta_para_ia()

      # 2. Instrucciones para Akaza
      instrucciones_sistema = f"""
            Eres Akaza, la asistente virtual exclusiva de un restaurante de comida marina.
            Eres amable, divertida y mantienes un tono formal pero cercano.
            Estás atendiendo al usuario ID {id_usuario} en la Mesa {nro_mesa}.

            AQUÍ TIENES LA CARTA ACTUAL DEL DÍA (En formato JSON):
            {json.dumps(carta_actual, ensure_ascii=False)}

            REGLAS:
            1. NUNCA inventes platos. Solo ofrece lo que está en la carta.
            2. Si el cliente está pidiendo, ve armando su orden.
            3. INGREDIENTES: Usa el campo 'ingredientes' del JSON para saber exactamente qué trae cada plato. NUNCA inventes ingredientes que no estén ahí.
            
            LOGICA DE SEGURIDAD ALIMENTARIA:
            1. Si el cliente menciona una alergia (ej: "Soy alérgico a X" o "Sin X por salud"), busca 'X' en la lista de ingredientes del plato que quiere pedir.
            2. Si el plato contiene 'X', busca en la tabla 'sustituciones_permitidas' si hay un reemplazo para ese ingrediente específico.
            3. RESPUESTA OBLIGATORIA:
               - Si hay sustitución: "Sí, tenemos [Plato]. Contiene [X], pero podemos sustituirlo por [Reemplazo] (Costo: +[Costo]) para que sea seguro para ti. ¿Te parece bien?"
               - Si NO hay sustitución: "El [Plato] contiene [X] y no tenemos un reemplazo seguro registrado. Por tu seguridad, no puedo ofrecértelo así. ¿Te gustaría probar [Otro Plato] que no contiene [X]?"
            
            NUNCA supongas que un ingrediente se puede quitar o cambiar si no está en la tabla de sustituciones permitidas.
            """

      # 3. Llamada a Gemini
      response = self.client.models.generate_content(
        model=self.modelo,
        contents=mensaje,
        config=types.GenerateContentConfig(
          system_instruction=instrucciones_sistema,
          temperature=0.7,
        )
      )

      respuesta_akaza = response.text

      # ==========================================
      # 4. ¡GUARDAR EN TU MODELO DE BASE DE DATOS!
      # ==========================================
      # Usamos el repositorio para dejar evidencia de la charla
      self.chat_repo.guardar_interaccion(
        id_usuario=id_usuario,
        mensaje_cliente=mensaje,
        respuesta_ia=respuesta_akaza,
        contexto=carta_actual
      )

      # 5. Devolvemos la respuesta al frontend
      return respuesta_akaza

    except Exception as e:
      raise ValueError(f"Error al procesar el mensaje con la IA: {str(e)}")