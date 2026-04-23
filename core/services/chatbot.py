import os
import json
import re
from typing import Optional
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
from dotenv import load_dotenv

from core.services.menu_service import MenuService
from core.services.pedido_service import PedidoService
from core.schemas.venta_schema import PedidoCreate
from infra.repository.chat_repo import ChatRepository

load_dotenv()


class ChatService:
  def __init__(self, db: Session):
    self.db = db
    self.menu_service = MenuService(db)
    self.chat_repo = ChatRepository(db)
    self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    self.modelo = "gemini-3-flash-preview"

  # 1. Hacemos que id_usuario y nro_mesa sean opcionales (pueden ser None)
  def procesar_mensaje(self, id_usuario: Optional[int], nro_mesa: Optional[int], mensaje: str) -> str:
    try:
      # Obtenemos la carta con ingredientes y sustituciones
      carta_actual = self.menu_service.obtener_carta_para_ia()

      # ==========================================
      # 2. DEFINIR EL MODO DEL CLIENTE (QR / VIP)
      # ==========================================
      reglas_especificas = ""

      if not nro_mesa:
        reglas_especificas = """
          ESTADO: Informativo (No ha escaneado QR).
          REGLA DE PEDIDOS: TIENES PROHIBIDO TOMAR PEDIDOS. Si intentan pedir, di: "Me encantaría tomar tu orden, pero por favor escanea el código QR de tu mesa primero."
          """
      elif nro_mesa and not id_usuario:
        reglas_especificas = f"""
          ESTADO: Cliente Casual en Mesa {nro_mesa}.
          REGLA DE PEDIDOS: Puedes tomar pedidos para la mesa {nro_mesa}.
          """
      elif nro_mesa and id_usuario:
        reglas_especificas = f"""
          ESTADO: Cliente VIP (ID: {id_usuario}) en Mesa {nro_mesa}.
          REGLA DE PEDIDOS: Toma pedidos con total confianza. Trátalo de forma especial.
          """

      # ==========================================
      # 3. CONSTRUIR EL CEREBRO DE AKAZA
      # ==========================================
      instrucciones_sistema = f"""
      Eres Akaza, la asistente virtual exclusiva de un restaurante de comida marina.
      Eres carismática, Divertida pero DIRECTA.

      {reglas_especificas}

      AQUÍ TIENES LA CARTA ACTUAL DEL DÍA (En formato JSON):
      {json.dumps(carta_actual, ensure_ascii=False)}

      REGLAS GENERALES, VISUALES Y DE COMPORTAMIENTO:
      1. BREVEDAD EXTREMA: Habla poco. Da respuestas cortas, precisas y al grano (máximo 2 líneas de texto). No escribas párrafos largos ni repitas saludos si ya estás conversando. El cliente tiene hambre, no lo aburras.
      2. RENDERIZADO VISUAL OBLIGATORIO: Cada vez que ofrezcas, recomiendes o menciones un plato, usa ESTRICTAMENTE este formato para que nuestro frontend dibuje la tarjeta con foto:
         ||Nombre - Precio - imagen_url||
         Ejemplo: "Te sugiero probar el ||Ceviche Clásico - 35.50 - https://rutatuya.com/ceviche.jpg||."
         (Usa el campo 'imagen_url' que viene en el JSON. Si el plato no tiene imagen en el JSON, usa la palabra 'null' en su lugar).
      3. NUNCA inventes platos ni ingredientes. Usa estrictamente el JSON proporcionado.
      4. ALERGIAS: Si mencionan una alergia, revisa los ingredientes.
         - Si tiene sustitución permitida: "Contiene [X], pero lo cambiamos por [Reemplazo] (+[Costo])."
         - Si NO tiene sustitución: "Contiene [X] y no es seguro. ¿Te sugiero [Otro Plato]?"
      5. CONFIRMACIÓN: Cuando armen el pedido, diles el total rápido y pregunta "¿Confirmo la orden?".
      6. INTERCEPTOR (SECRETO): Cuando el usuario confirme que está de acuerdo con su orden, incluye OBLIGATORIAMENTE al final de tu mensaje:
         [ORDEN_CONFIRMADA] {{"detalles": [{{"plato_ref": 3, "cantidad": 2}}]}}
      """

      # ==========================================
      # 4. RECONSTRUIR LA MEMORIA (HISTORIAL)
      # ==========================================
      # Buscamos el historial. (Asegúrate de que tu repo acepte id_usuario o nro_mesa para buscar)
      mensajes_previos = self.chat_repo.obtener_historial_reciente(id_usuario=id_usuario, nro_mesa=nro_mesa, limite=4)

      historial_gemini = []

      for msg in mensajes_previos:
        historial_gemini.append(types.Content(role="user", parts=[types.Part.from_text(text=msg.mensaje_cliente)]))
        historial_gemini.append(types.Content(role="model", parts=[types.Part.from_text(text=msg.respuesta_ia)]))

      # Añadimos el mensaje actual al final del hilo
      historial_gemini.append(types.Content(role="user", parts=[types.Part.from_text(text=mensaje)]))

      # ==========================================
      # 5. LLAMADA A GEMINI CON EL HISTORIAL COMPLETO
      # ==========================================
      response = self.client.models.generate_content(
        model=self.modelo,
        contents=historial_gemini,  # Pasamos la lista completa, no solo el string
        config=types.GenerateContentConfig(
          system_instruction=instrucciones_sistema,
          temperature=0.7,
        )
      )

      respuesta_akaza = response.text or ""

      # ==========================================
      # 6. INTERCEPTOR DE PEDIDOS CONFIRMADOS
      # ==========================================
      etiqueta_orden = "[ORDEN_CONFIRMADA]"
      if etiqueta_orden in respuesta_akaza:
        try:
          if nro_mesa is None:
            raise ValueError("No se puede registrar pedido confirmado sin número de mesa.")

          _, bloque_orden = respuesta_akaza.split(etiqueta_orden, 1)
          bloque_orden = bloque_orden.strip()
          if not bloque_orden:
            raise ValueError("La IA emitió la etiqueta de confirmación sin JSON.")

          orden_data = json.loads(bloque_orden)
          if not isinstance(orden_data, dict):
            raise ValueError("El JSON de la orden confirmada no es un objeto válido.")
          if "detalles" not in orden_data:
            raise ValueError("El JSON de la orden confirmada no contiene 'detalles'.")

          pedido_service = PedidoService(self.db)
          payload_pedido = PedidoCreate(
            id_usuario=id_usuario,
            nro_mesa=nro_mesa,
            detalles=orden_data["detalles"],
          )
          pedido_service.registrar_nuevo_pedido(payload_pedido)

          # Limpiamos la etiqueta y el JSON para que el frontend solo vea texto amigable.
          respuesta_akaza = re.sub(
            r"\s*\[ORDEN_CONFIRMADA\].*$",
            "",
            respuesta_akaza,
            flags=re.DOTALL,
          ).strip()
        except (json.JSONDecodeError, TypeError, ValueError) as e:
          # Nunca exponemos el bloque secreto al cliente final.
          respuesta_akaza = re.sub(
            r"\s*\[ORDEN_CONFIRMADA\].*$",
            "",
            respuesta_akaza,
            flags=re.DOTALL,
          ).strip()
          if not respuesta_akaza:
            respuesta_akaza = "Tu pedido fue confirmado, pero ocurrió un problema al procesarlo. ¿Puedes reenviarlo, por favor?"
          print(f"[InterceptorPedido] Error controlado: {e}")

      # ==========================================
      # 7. GUARDAR LA INTERACCIÓN
      # ==========================================
      # Guardamos enviando también el nro_mesa para no perder el rastro de los clientes casuales
      self.chat_repo.guardar_interaccion(
        id_usuario=id_usuario,
        nro_mesa=nro_mesa,
        mensaje_cliente=mensaje,
        respuesta_ia=respuesta_akaza,
        contexto=carta_actual
      )

      return respuesta_akaza

    except Exception as e:
      raise ValueError(f"Error al procesar el mensaje con la IA: {str(e)}")