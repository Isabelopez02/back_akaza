from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import settings
from sqlalchemy import create_engine

# 1. la conexión físic-a a PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# 2. Hace consultas a la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Todas las tablas (clases) heredarán de esto
Base=declarative_base()

# 4. Dependencia para FastAPI (Abre y cierra la conexión por cada petición web)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()