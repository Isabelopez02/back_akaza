from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# Engine configuration for PostgreSQL connection
engine = create_engine(settings.DATABASE_URL)

# Session factory for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for data models
Base = declarative_base()

def get_db():
    """Dependency generator for database sessions used in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes the database by creating tables, applying migrations, and seeding data."""
    from infra.db.models import __init__  # Ensure models are imported for metadata registration
    Base.metadata.create_all(bind=engine)
    
    # Safe incremental schema migrations
    try:
        with engine.connect() as conn:
            # Pedidos table migrations
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS ticket VARCHAR(50);"))
            
            # ComprasClientes table migrations
            conn.execute(text("ALTER TABLE compras_clientes ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(50) DEFAULT 'EFECTIVO';"))
            conn.execute(text("ALTER TABLE compras_clientes ADD COLUMN IF NOT EXISTS monto_efectivo DECIMAL(10,2) DEFAULT 0.0;"))
            conn.execute(text("ALTER TABLE compras_clientes ADD COLUMN IF NOT EXISTS monto_yape DECIMAL(10,2) DEFAULT 0.0;"))
            conn.execute(text("ALTER TABLE compras_clientes ADD COLUMN IF NOT EXISTS monto_tarjeta DECIMAL(10,2) DEFAULT 0.0;"))
            
            conn.commit()
    except Exception as e:
        print(f"[DB Migrations] Error applying column migrations: {e}")

    # Seed base roles and administrator accounts if missing
    try:
        from infra.db.seed import seed
        seed()
    except Exception as e:
        print(f"[DB Seeding] Error running initial database seed: {e}")