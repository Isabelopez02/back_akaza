import sys
sys.path.append(".")

from infra.db.database import SessionLocal
from core.services.chatbot import ChatService

db = SessionLocal()
try:
    chat_service = ChatService(db)
    print("Iniciando prueba in-memory de procesar_mensaje...")
    res = chat_service.procesar_mensaje(
        id_usuario=8,
        nro_mesa=5,
        mensaje="Hola, soy el cliente logueado. Quiero pedir 1 Ceviche Akaza para mi mesa 5 por favor"
    )
    print("RESULTADO:", res)
except Exception as e:
    import traceback
    print("TRACEBACK ERROR DETECTADO:")
    traceback.print_exc()
finally:
    db.close()
