from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infra.db.database import init_db

# Importar enrutadores
from api.router import router as chat_router
from api.routes import menu_router, pedido_router, inventario_router
from api.routes.compras_router import router as compras_router
from api.routes.auth import auth_router
from api.routes.admin_platos_router import router as admin_platos_router
from api.routes.admin.admin_combos_router import router as admin_combos_router
from api.routes.admin.admin_usuarios_router import router as admin_usuarios_router
from api.routes.dashboard_router import router as dashboard_router
from core.services.telegram_service import router as telegram_router

# Inicializar las tablas de la base de datos y ejecutar las migraciones necesarias
init_db()

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="AKAZA - Backend Restaurante & IA",
    description="Chatbot de Akaza y Sistema ERP",
    version="1.0.0"
)

# Configuración del middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar enrutadores
app.include_router(chat_router)
app.include_router(menu_router.router)
app.include_router(pedido_router.router)
app.include_router(inventario_router.router)
app.include_router(compras_router)
app.include_router(auth_router.router)
app.include_router(admin_platos_router, prefix="/api/admin")
app.include_router(admin_combos_router, prefix="/api/admin")
app.include_router(admin_usuarios_router, prefix="/api/admin")
app.include_router(dashboard_router)
app.include_router(telegram_router)

@app.get("/test/debug")
async def debug_test():
    """Endpoint de depuración para verificar la capacidad de respuesta del backend."""
    return {
        "status": "OK",
        "message": "Backend is running",
        "cors_check": "CORS allowed",
        "timestamp": "2026-05-07"
    }

@app.get("/")
def health_check():
    """Endpoint de verificación de estado para comprobar la conexión a la base de datos y la activación de rutas."""
    return {
        "estado": "OK",
        "mensaje": "¡El servidor de AKAZA está abierto, conectado a Postgres y con todas las rutas activas!"
    }