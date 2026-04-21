from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infra.db.database import engine, Base
from infra.db import models

# 🔥 1. Importa tu ruta del chatbot (Asegúrate de que la ruta coincida con tu archivo)
# Le ponemos el alias 'chat_router' para que no haya confusiones
from api.router import router as chat_router

# 🔥 2. Importa los 3 nuevos routers del sistema ERP
from api.routes import menu_router, pedido_router, inventario_router

# Lee los modelos y crea las tablas automáticamente
Base.metadata.create_all(bind=engine)

# Inicializamos la aplicación FastAPI (Nuestro restaurante)
app = FastAPI(
    title="AKAZA - Backend Restaurante & IA",
    description="Chatbot de Akaza y Sistema ERP",
    version="1.0.0"
)

# Configuración de CORS (Para que tu frontend en Next.js pueda hacerle peticiones)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiarás el "*" por la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🚀 REGISTRO DE RUTAS (ENDPOINTS)
# ==========================================

# 1. Ruta de tu IA / Chatbot original
app.include_router(chat_router)

# 2. Rutas del Sistema ERP que acabamos de armar
app.include_router(menu_router.router)
app.include_router(pedido_router.router)
app.include_router(inventario_router.router)

# ==========================================

# Endpoint de prueba (El saludo de bienvenida)
@app.get("/")
def health_check():
    return {
        "estado": "OK",
        "mensaje": "¡El servidor de AKAZA está abierto, conectado a Postgres y con todas las rutas activas!"
    }