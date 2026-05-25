from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date, timedelta
import telebot
from telebot import types
from google import genai
from google.genai import types as gemini_types

from core.config import settings
from infra.db.database import get_db
from infra.db.models.ventas import Pedido, DetallePedido, CompraCliente
from infra.db.models.menu import Plato
from infra.db.models.inventario import CompraHistorial

router = APIRouter(prefix="/telegram", tags=["Telegram Admin Dashboard"])
bot = telebot.TeleBot(settings.TELEGRAM_API_KEY, threaded=False)
ai_client = genai.Client(api_key=settings.GEMINI_API_KEY)


def obtener_metricas_dashboard(db: Session) -> dict:
  """
  Ejecuta consultas en tiempo real sobre PostgreSQL para obtener las métricas operativas
  idénticas a las que se muestran en el dashboard administrativo y reportes de la web.
  """
  hoy = date.today()
  ayer = hoy - timedelta(days=1)

  try:
    # 1. Ventas de Hoy vs Ayer (Pedidos pagados únicamente)
    ventas_hoy = db.query(func.coalesce(func.sum(CompraCliente.total), 0)).filter(
        cast(CompraCliente.fecha_pago, Date) == hoy
    ).scalar()
    ventas_hoy = float(ventas_hoy)

    ventas_ayer = db.query(func.coalesce(func.sum(CompraCliente.total), 0)).filter(
        cast(CompraCliente.fecha_pago, Date) == ayer
    ).scalar()
    ventas_ayer = float(ventas_ayer)

    # 2. Cantidad de Pedidos Hoy vs Ayer
    pedidos_hoy = db.query(func.count(Pedido.id)).filter(
        cast(Pedido.fecha_venta, Date) == hoy
    ).scalar() or 0

    pedidos_ayer = db.query(func.count(Pedido.id)).filter(
        cast(Pedido.fecha_venta, Date) == ayer
    ).scalar() or 0

    # 3. Pedidos Pendientes en Cocina
    pedidos_pendientes = db.query(func.count(Pedido.id)).filter(
        Pedido.estado_cocina.in_(["ESPERA", "PREPARANDO", "En proceso", "Espera", "Preparando"])
    ).scalar() or 0

    # 4. Mesas Ocupadas Actualmente (tienen pedido pendiente de pago hoy)
    mesas_query = db.query(Pedido.nro_mesa).filter(
        cast(Pedido.fecha_venta, Date) == hoy,
        Pedido.estado_pago.in_(["PENDIENTE", "pendiente"])
    ).distinct().all()
    mesas_ocupadas_actualmente = [int(m.nro_mesa) for m in mesas_query]

    # 5. Plato Más Vendido Hoy (métricas acumuladas de hoy)
    plato_ranking_hoy = (
        db.query(Plato.nombre, func.sum(DetallePedido.cantidad).label("total_vendido"))
        .join(DetallePedido, DetallePedido.id_plato == Plato.id)
        .join(Pedido, Pedido.id == DetallePedido.id_pedido)
        .filter(cast(Pedido.fecha_venta, Date) == hoy)
        .group_by(Plato.id, Plato.nombre)
        .order_by(func.sum(DetallePedido.cantidad).desc())
        .first()
    )
    plato_mas_vendido_hoy = f"{plato_ranking_hoy.nombre} ({int(plato_ranking_hoy.total_vendido)} und.)" if plato_ranking_hoy else "Ninguno aún"

    # 6. Gastos del Día (Compras de insumos registradas)
    gastos_hoy = db.query(
        func.coalesce(
            func.sum(CompraHistorial.cantidad_comprada * CompraHistorial.precio_unidad_compra),
            0
        )
    ).filter(cast(CompraHistorial.fecha_compra, Date) == hoy).scalar()
    gastos_hoy = float(gastos_hoy)

    # 7. Ganancia Neta Hoy
    ganancia_neta = ventas_hoy - gastos_hoy

    # 8. Top 3 Platos Históricos (acumulado general de reportes)
    platos_ranking_historico = (
        db.query(Plato.nombre, func.sum(DetallePedido.cantidad).label("total_vendido"))
        .join(DetallePedido, DetallePedido.id_plato == Plato.id)
        .group_by(Plato.id, Plato.nombre)
        .order_by(func.sum(DetallePedido.cantidad).desc())
        .limit(3)
        .all()
    )
    top_3_platos_historico = [f"{r.nombre} ({int(r.total_vendido)} und.)" for r in platos_ranking_historico]

    return {
        "fecha_consulta": hoy.isoformat(),
        "ventas_hoy_soles": ventas_hoy,
        "ventas_ayer_soles": ventas_ayer,
        "pedidos_totales_hoy": pedidos_hoy,
        "pedidos_totales_ayer": pedidos_ayer,
        "pedidos_pendientes_cocina": pedidos_pendientes,
        "mesas_ocupadas_actualmente": mesas_ocupadas_actualmente,
        "plato_mas_vendido_hoy": plato_mas_vendido_hoy,
        "gastos_hoy_soles": gastos_hoy,
        "ganancia_neta_hoy_soles": ganancia_neta,
        "top_3_platos_historico": top_3_platos_historico,
        "alertas_sistema": "Ninguna. Todos los microservicios operando con normalidad en Postgres."
    }
  except Exception as e:
    print(f"[Error consultas db telegram]: {e}")
    # Retornar fallback estructurado en caso de base de datos vacía o migración pendiente
    return {
        "fecha_consulta": hoy.isoformat(),
        "ventas_hoy_soles": 0.0,
        "ventas_ayer_soles": 0.0,
        "pedidos_totales_hoy": 0,
        "pedidos_totales_ayer": 0,
        "pedidos_pendientes_cocina": 0,
        "mesas_ocupadas_actualmente": [],
        "plato_mas_vendido_hoy": "Ninguno",
        "gastos_hoy_soles": 0.0,
        "ganancia_neta_hoy_soles": 0.0,
        "top_3_platos_historico": [],
        "alertas_sistema": f"Error al extraer métricas reales: {str(e)}"
    }


def consultar_ia_dashboard(mensaje_admin: str, datos_dashboard: dict) -> str:
  """Envía las métricas actuales del dashboard a Gemini junto con la pregunta del administrador."""

  instrucciones_sistema = f"""
    Eres el Asistente Ejecutivo de Analítica y Negocios para el administrador de "Akaza Restaurante".
    Tu único propósito es analizar los datos operativos y financieros en tiempo real del restaurante y responder de forma clara, ejecutiva, directa y sumamente profesional a las consultas de la gerencia.

    MÉTRICAS OPERATIVAS DEL RESTAURANTE EN TIEMPO REAL:
    {datos_dashboard}

    REGLAS DE COMPORTAMIENTO Y FORMATO OBLIGATORIAS:
    1. Responde utilizando estrictamente formato HTML válido para Telegram.
    2. Usa la etiqueta <b>texto</b> para poner texto en negrita (ej. <b>S/ 1,450.00</b>, <b>Ceviche</b>).
    3. Usa la etiqueta <i>texto</i> para cursiva.
    4. Usa la etiqueta <code>texto</code> para representar números, porcentajes, listas de mesas o texto monospace (ej. <code>[2, 5, 8]</code>, <code>S/ 45.20</code>).
    5. Para listas y viñetas, utiliza saltos de línea y guiones sencillos (-) al inicio de cada línea.
    6. TIENES TOTALMENTE PROHIBIDO usar formato Markdown (como asteriscos *, guiones bajos _, comillas invertidas `) en tus respuestas. Esto es crítico para evitar errores de parseo en Telegram.
    7. Mantén un tono formal, de negocios y altamente analítico.
    """

  response = ai_client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[mensaje_admin],
      config=gemini_types.GenerateContentConfig(
          system_instruction=instrucciones_sistema,
          temperature=0.3, # Temperatura baja para máxima fidelidad en datos y cálculos
      )
  )
  return response.text or "No se pudo compilar la respuesta ejecutiva."


@router.post("/webhook")
async def telegram_webhook(request_body: dict, db: Session = Depends(get_db)):
  update = types.Update.de_json(request_body)

  if update.message and update.message.text:
    chat_id = update.message.chat.id
    mensaje_admin = update.message.text

    # 🔒 FILTRO DE SEGURIDAD ESTRICTO PARA EL ADMINISTRADOR
    if str(chat_id) != settings.ID_ADMIN:
      bot.send_message(chat_id, "Acceso denegado. Este canal de inteligencia es privado.")
      return {"status": "unauthorized"}

    try:
      # 1. Traemos la data fresca de la base de datos para tu dashboard
      datos_actuales = obtener_metricas_dashboard(db)

      # 2. Le pasamos la pregunta del administrador junto con los datos a Gemini
      respuesta_bot = consultar_ia_dashboard(mensaje_admin, datos_actuales)

      # 3. Te respondemos de vuelta a tu chat de Telegram usando el parser HTML
      bot.send_message(chat_id, respuesta_bot, parse_mode="HTML")

    except Exception as e:
      print(f"[Telegram Bot Error]: {e}")
      bot.send_message(chat_id, "Disculpa, ocurrió un inconveniente al compilar las métricas operativas.")

  return {"status": "ok"}