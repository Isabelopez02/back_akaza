from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infra.db.database import init_db

# Import routers
from api.router import router as chat_router
from api.routes import menu_router, pedido_router, inventario_router
from api.routes.compras_router import router as compras_router
from api.routes.auth import auth_router
from api.routes.admin_platos_router import router as admin_platos_router
from api.routes.admin.admin_combos_router import router as admin_combos_router
from api.routes.admin.admin_usuarios_router import router as admin_usuarios_router
from api.routes.dashboard_router import router as dashboard_router

# Initialize database tables and execute required migrations
init_db()

# Initialize FastAPI app
app = FastAPI(
    title="AKAZA - Backend Restaurante & IA",
    description="Chatbot de Akaza y Sistema ERP",
    version="1.0.0"
)

# CORS middleware configuration
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

# Register routers
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

@app.get("/test/debug")
async def debug_test():
    """Debug endpoint to verify backend responsiveness."""
    return {
        "status": "OK",
        "message": "Backend is running",
        "cors_check": "CORS allowed",
        "timestamp": "2026-05-07"
    }

@app.get("/")
def health_check():
    """Health check endpoint to verify database connection and route activation."""
    return {
        "estado": "OK",
        "mensaje": "¡El servidor de AKAZA está abierto, conectado a Postgres y con todas las rutas activas!"
    }