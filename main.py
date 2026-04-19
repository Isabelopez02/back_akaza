from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infra.db.database import engine, Base
from infra.db import models

#Importa las rutas
from api.router import router

# Lee los modelos y crea las tablas automáticamente
Base.metadata.create_all(bind=engine)

# Inicializamos la aplicación FastAPI (Nuestro restaurante)
app = FastAPI(
    title="AKAZA - Backend Restaurante & IA",
    description="chatbot de Akaza",
    version="1.0.0"
)

# Configuración de CORS (Para que tu frontend pueda hacerle peticiones sin que lo bloquee)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiarás el "*" por la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta del chatbot
app.include_router(router)

# Endpoint de prueba (El saludo de bienvenida)
@app.get("/")
def health_check():
    return {
        "estado": "OK",
        "mensaje": "¡El servidor de AKAZA está abierto y conectado Postgres!"
    }