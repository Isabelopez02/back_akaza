import os
import json
import re
from typing import Optional
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
import requests
from dotenv import load_dotenv

from core.services.menu_service import MenuService
from core.services.pedido_service import PedidoService
from core.schemas.venta_schema import PedidoCreate
from infra.repository.chat_repo import ChatRepository

load_dotenv()

class ChatService:
  """Maneja el procesamiento del lenguaje natural (NLP) con Azure AI Foundry (GPT-4o) y respaldo con Gemini."""

  def __init__(self, db: Session):
    self.db = db
    self.menu_service = MenuService(db)
    self.chat_repo = ChatRepository(db)
    
    # Parámetros de Azure AI Foundry (GPT-4o)
    self.azure_key = os.getenv("AZURE_AI_KEY")
    self.azure_endpoint = os.getenv("AZURE_AI_ENDPOINT", "https://akaza-ai-resource.openai.azure.com/openai/v1")
    self.azure_deployment = os.getenv("AZURE_AI_DEPLOYMENT", "gpt-4o")

    # Respaldo con Google Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
      try:
        self.client = genai.Client(api_key=gemini_key)
        self.modelo = "gemini-2.5-flash"
      except Exception:
        self.client = None
    else:
      self.client = None

  def procesar_mensaje(self, id_usuario: Optional[int], nro_mesa: Optional[int], mensaje: str) -> str:
    """Procesa la entrada del usuario usando Azure AI Foundry (o Gemini) y captura los pedidos."""
    try:
      # Recuperar el catálogo activo con recetas y sustituciones permitidas
      carta_actual = self.menu_service.obtener_carta_para_ia()

      # Comprobar si la mesa ya tiene un pedido pendiente activo
      tiene_pedido_activo = False
      ticket_activo = ""
      if nro_mesa:
        from infra.db.models.ventas import Pedido
        pedido_pendiente = self.db.query(Pedido).filter(
            Pedido.nro_mesa == nro_mesa,
            Pedido.estado_pago == "PENDIENTE",
            Pedido.estado_cocina != "CANCELADO"
        ).first()
        if pedido_pendiente:
          tiene_pedido_activo = True
          ticket_activo = pedido_pendiente.ticket or f"ORD-{pedido_pendiente.id}"

      # Definir el contexto y las restricciones basadas en la autenticación del cliente y el tipo de sesión
      reglas_especificas = ""

      if not nro_mesa:
        reglas_especificas = """
          ESTADO: Informativo (No ha escaneado QR).
          REGLAS DE PEDIDOS:
          - TIENES TOTALMENTE PROHIBIDO TOMAR PEDIDOS, CONFIRMAR ÓRDENES O GENERAR DETALLES DE PEDIDO.
          - Puedes mostrar, sugerir y ofrecer libremente información detallada sobre los platos y combos del menú de hoy.
          - Si el usuario intenta ordenar, pedir, confirmar o armar un pedido, debes indicarle de forma amable y directa: "Me encantaría tomar tu orden, pero por favor escanea el código QR de tu mesa primero para poder registrarla."
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

      if tiene_pedido_activo:
        reglas_especificas += f"""
          ALERTA MESA OCUPADA: La mesa {nro_mesa} ya tiene un pedido activo y pendiente de pago ({ticket_activo}).
          REGLAS OBLIGATORIAS:
          - En tu primer mensaje donde se mencione ordenar, DEBES advertir cordialmente y preguntar: "Veo que la mesa {nro_mesa} ya tiene un pedido activo ({ticket_activo}). ¿Deseas realizar otro pedido para esta misma mesa?"
          - Si el cliente confirma explícitamente que sí desea realizar otro pedido para la misma mesa, entonces procede a armar la orden normalmente y confírmala cuando te dé el visto bueno.
          - Si responde que no, dile que de acuerdo y quédate atento a otras consultas.
          """

      # Construir las instrucciones principales del sistema para el LLM
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

      # Reconstruir el historial de diálogo (memoria) para preservar el contexto
      mensajes_previos = self.chat_repo.obtener_historial_reciente(id_usuario=id_usuario, nro_mesa=nro_mesa, limite=4)
      respuesta_akaza = ""

      # 1. Intentar llamar a Azure AI Foundry (GPT-4o)
      if self.azure_key:
        try:
          azure_messages = [{"role": "system", "content": instrucciones_sistema}]
          for msg in mensajes_previos:
            azure_messages.append({"role": "user", "content": msg.mensaje_cliente})
            azure_messages.append({"role": "assistant", "content": msg.respuesta_ia})
          azure_messages.append({"role": "user", "content": mensaje})

          endpoint_clean = self.azure_endpoint.rstrip("/")
          if endpoint_clean.endswith("/openai/v1") or "/openai/v1" in endpoint_clean:
            url = f"{endpoint_clean}/chat/completions"
            payload = {
              "model": self.azure_deployment,
              "messages": azure_messages,
              "temperature": 0.7,
              "max_tokens": 800
            }
          else:
            url = f"{endpoint_clean}/openai/deployments/{self.azure_deployment}/chat/completions?api-version=2024-08-01-preview"
            payload = {
              "messages": azure_messages,
              "temperature": 0.7,
              "max_tokens": 800
            }

          headers = {
            "api-key": self.azure_key,
            "Authorization": f"Bearer {self.azure_key}",
            "Content-Type": "application/json"
          }
          resp = requests.post(url, headers=headers, json=payload, timeout=20)
          if resp.status_code == 200:
            data = resp.json()
            respuesta_akaza = data["choices"][0]["message"]["content"]
          else:
            print(f"[Azure AI Foundry] Error {resp.status_code}: {resp.text}")
        except Exception as e:
          print(f"[Azure AI Foundry] Excepción al invocar agente: {e}")

      # 2. Respaldo automático con Google Gemini si Azure no está configurado o falla
      if not respuesta_akaza and self.client:
        try:
          historial_gemini = []
          for msg in mensajes_previos:
            historial_gemini.append(types.Content(role="user", parts=[types.Part.from_text(text=msg.mensaje_cliente)]))
            historial_gemini.append(types.Content(role="model", parts=[types.Part.from_text(text=msg.respuesta_ia)]))
          historial_gemini.append(types.Content(role="user", parts=[types.Part.from_text(text=mensaje)]))

          response = self.client.models.generate_content(
            model=self.modelo,
            contents=historial_gemini,
            config=types.GenerateContentConfig(
              system_instruction=instrucciones_sistema,
              temperature=0.7,
            )
          )
          respuesta_akaza = response.text or ""
        except Exception as e:
          print(f"[Gemini Fallback] Error: {e}")

      if not respuesta_akaza:
        respuesta_akaza = "¡Hola! Estoy experimentando una breve interrupción en mi sistema de cocina. ¿Podrías consultarme de nuevo en un segundo?"

      # Comprobar si hay un bloque estructurado [ORDEN_CONFIRMADA] en la salida del modelo
      etiqueta_orden = "[ORDEN_CONFIRMADA]"
      if etiqueta_orden in respuesta_akaza:
        try:
          if nro_mesa is None:
            raise ValueError("Mesa no especificada para registrar pedido.")

          _, bloque_orden = respuesta_akaza.split(etiqueta_orden, 1)
          bloque_orden = bloque_orden.strip()
          if not bloque_orden:
            raise ValueError("Falta el bloque JSON de la orden confirmada.")

          orden_data = json.loads(bloque_orden)
          if not isinstance(orden_data, dict):
            raise ValueError("El JSON no es un objeto.")
          if "detalles" not in orden_data:
            raise ValueError("Falta campo 'detalles' en la orden.")

          pedido_service = PedidoService(self.db)
          payload_pedido = PedidoCreate(
            id_usuario=id_usuario,
            nro_mesa=nro_mesa,
            detalles=orden_data["detalles"],
          )
          pedido_service.registrar_nuevo_pedido(payload_pedido)

          # Limpiar las etiquetas de comandos y metadatos antes de retornar al usuario
          respuesta_akaza = re.sub(
            r"\s*\[ORDEN_CONFIRMADA\].*$",
            "",
            respuesta_akaza,
            flags=re.DOTALL,
          ).strip()
        except (json.JSONDecodeError, TypeError, ValueError) as e:
          # Alternativa y limpieza de la etiqueta de salida si ocurre un error durante el análisis
          respuesta_akaza = re.sub(
            r"\s*\[ORDEN_CONFIRMADA\].*$",
            "",
            respuesta_akaza,
            flags=re.DOTALL,
          ).strip()
          if not respuesta_akaza:
            respuesta_akaza = "Tu pedido fue confirmado, pero ocurrió un problema al procesarlo. ¿Puedes reenviarlo, por favor?"
          print(f"[InterceptorPedido] Error: {e}")

      # Guardar el registro de interacción en el repositorio
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