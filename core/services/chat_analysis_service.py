import os
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from google import genai
from infra.db.models.chat import IAHistorialChat
from dotenv import load_dotenv

load_dotenv()


class ChatAnalysisService:
    """Servicio para analizar los chats de clientes y extraer insights."""

    def __init__(self, db: Session):
        self.db = db
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.modelo = "gemini-2.5-flash"

    def obtener_mensajes_recientes(self, dias: int = 7, limite: int = 500) -> List[IAHistorialChat]:
        """Obtiene los últimos mensajes de clientes de los últimos N días."""
        try:
            fecha_inicio = datetime.utcnow() - timedelta(days=dias)
            
            mensajes = (
                self.db.query(IAHistorialChat)
                .filter(IAHistorialChat.fecha_interaccion >= fecha_inicio)
                .order_by(IAHistorialChat.fecha_interaccion.desc())
                .limit(limite)
                .all()
            )
            return mensajes
        except Exception as e:
            raise ValueError(f"Error al obtener mensajes: {str(e)}")

    def obtener_estadisticas_basicas(self, dias: int = 7) -> Dict:
        """Calcula estadísticas básicas de interacciones."""
        try:
            fecha_inicio = datetime.utcnow() - timedelta(days=dias)
            
            # Total de mensajes
            total_mensajes = (
                self.db.query(IAHistorialChat)
                .filter(IAHistorialChat.fecha_interaccion >= fecha_inicio)
                .count()
            )
            
            # Usuarios únicos
            usuarios_unicos = (
                self.db.query(IAHistorialChat.id_usuario)
                .filter(
                    IAHistorialChat.fecha_interaccion >= fecha_inicio,
                    IAHistorialChat.id_usuario.isnot(None)
                )
                .distinct()
                .count()
            )
            
            # Mesas únicas
            mesas_unicas = (
                self.db.query(IAHistorialChat.nro_mesa)
                .filter(
                    IAHistorialChat.fecha_interaccion >= fecha_inicio,
                    IAHistorialChat.nro_mesa.isnot(None)
                )
                .distinct()
                .count()
            )
            
            return {
                "total_mensajes": total_mensajes,
                "usuarios_unicos": usuarios_unicos,
                "mesas_unicas": mesas_unicas,
                "periodo_dias": dias
            }
        except Exception as e:
            raise ValueError(f"Error al calcular estadísticas: {str(e)}")

    def analizar_preguntas_frecuentes(self, dias: int = 7) -> str:
        """Usa IA para analizar las preguntas más frecuentes de clientes."""
        try:
            mensajes = self.obtener_mensajes_recientes(dias=dias, limite=100)
            
            if not mensajes:
                return "No hay suficientes datos para analizar aún."
            
            # Compilar todos los mensajes
            texto_mensajes = "\n".join([f"- {msg.mensaje_cliente}" for msg in mensajes])
            
            prompt = f"""
Analiza los siguientes mensajes de clientes de un restaurante y extrae LAS 5 PREGUNTAS O TEMAS MÁS FRECUENTES.
Para cada tema, indica:
1. El tema/pregunta
2. Cuántas veces aproximadamente aparece
3. Ejemplos de lo que preguntan

MENSAJES:
{texto_mensajes}

Responde en HTML válido para Telegram:
- Usa <b>tema</b> para resaltar
- Usa <code>cifras</code> para números
- Usa saltos de línea \\n para separar temas
"""

            response = self.client.models.generate_content(
                model=self.modelo,
                contents=[prompt]
            )
            
            return response.text
        except Exception as e:
            return f"Error al analizar preguntas: {str(e)}"

    def analizar_opiniones_clientes(self, dias: int = 7) -> str:
        """Analiza las opiniones y sentimientos generales de los clientes."""
        try:
            mensajes = self.obtener_mensajes_recientes(dias=dias, limite=100)
            
            if not mensajes:
                return "No hay suficientes datos para analizar aún."
            
            # Compilar todos los mensajes
            texto_mensajes = "\n".join([f"- {msg.mensaje_cliente}" for msg in mensajes])
            
            prompt = f"""
Analiza el tono y sentimiento general en estos mensajes de clientes de un restaurante.
Identifica:
1. Sentimiento general (Positivo/Negativo/Neutral)
2. Principales quejas o insatisfacciones (si las hay)
3. Aspectos que más les gustan
4. Sugerencias de mejora implícitas
5. Nivel de satisfacción general (escala 1-10)

MENSAJES:
{texto_mensajes}

Responde en HTML válido para Telegram:
- Usa <b>encabezados</b> en negrita
- Usa <i>anotaciones</i> en cursiva
- Usa <code>números</code> para métricas
- Usa saltos de línea \\n para separar secciones
"""

            response = self.client.models.generate_content(
                model=self.modelo,
                contents=[prompt]
            )
            
            return response.text
        except Exception as e:
            return f"Error al analizar opiniones: {str(e)}"

    def analizar_platos_mencionados(self, dias: int = 7) -> str:
        """Analiza cuáles son los platos más mencionados y solicitados."""
        try:
            mensajes = self.obtener_mensajes_recientes(dias=dias, limite=150)
            
            if not mensajes:
                return "No hay suficientes datos para analizar aún."
            
            # Compilar todos los mensajes
            texto_mensajes = "\n".join([f"- {msg.mensaje_cliente}" for msg in mensajes])
            
            prompt = f"""
Analiza estos mensajes de clientes y extrae:
1. Los platos más mencionados (con frecuencia aproximada)
2. Platos que reciben más elogios
3. Platos con quejas o críticas
4. Combinaciones populares que piden juntas
5. Pedidos especiales o modificaciones frecuentes

MENSAJES:
{texto_mensajes}

Responde en HTML válido para Telegram:
- Usa <b>nombres de platos</b> en negrita
- Usa <code>números</code> para menciones
- Usa saltos de línea \\n para separar secciones
- Sé específico y directo
"""

            response = self.client.models.generate_content(
                model=self.modelo,
                contents=[prompt]
            )
            
            return response.text
        except Exception as e:
            return f"Error al analizar platos: {str(e)}"

    def responder_pregunta_chat(self, pregunta_admin: str, dias: int = 7) -> str:
        """Responde preguntas ejecutivas sobre la actividad de clientes por chat/Telegram."""
        try:
            stats = self.obtener_estadisticas_basicas(dias=dias)
            mensajes = self.obtener_mensajes_recientes(dias=dias, limite=100)

            if not mensajes:
                return "No hay suficientes datos de chat para responder esta consulta."

            texto_mensajes = "\n".join([f"- {msg.mensaje_cliente}" for msg in mensajes[:50]])

            prompt = f"""
Eres un asistente ejecutivo para el administrador de Akaza Restaurante.
Tienes datos de actividad de chat/Telegram de clientes y debes responder de forma clara, breve y con formato HTML válido para Telegram.

Datos disponibles:
- Mensajes totales últimos {dias} días: {stats['total_mensajes']}
- Usuarios únicos: {stats['usuarios_unicos']}
- Mesas únicas: {stats['mesas_unicas']}

Ejemplos de mensajes recientes:
{texto_mensajes}

Pregunta del administrador: {pregunta_admin}

Responde con un texto directo, menciona cifras cuando correspondan y usa HTML válido para Telegram:
- <b>texto</b> para negritas
- <code>texto</code> para números y datos clave
- separa secciones con saltos de línea
"""

            response = self.client.models.generate_content(
                model=self.modelo,
                contents=[prompt]
            )
            return response.text or "No se pudo procesar la consulta de chat en este momento."
        except Exception as e:
            return f"Error al responder pregunta de chat: {str(e)}"

    def generar_reporte_completo(self, dias: int = 7) -> str:
        """Genera un reporte ejecutivo completo con todos los análisis."""
        try:
            stats = self.obtener_estadisticas_basicas(dias=dias)
            
            reporte = f"""
<b>📊 REPORTE DE ANÁLISIS DE CHATS - ÚLTIMOS {dias} DÍAS</b>

<b>📈 ESTADÍSTICAS GENERALES:</b>
- Total de mensajes: <code>{stats['total_mensajes']}</code>
- Usuarios activos: <code>{stats['usuarios_unicos']}</code>
- Mesas atendidas: <code>{stats['mesas_unicas']}</code>

<b>🔍 ANÁLISIS EN DETALLE:</b>

Para obtener análisis detallado, usa los comandos:
- /chat_preguntas - Preguntas más frecuentes
- /chat_opiniones - Opiniones y sentimientos
- /chat_platos - Platos más mencionados
"""
            
            return reporte
        except Exception as e:
            return f"Error al generar reporte: {str(e)}"
