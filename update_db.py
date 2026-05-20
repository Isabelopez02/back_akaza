import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infra.db.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS ticket VARCHAR(50);"))
        conn.commit()
    print("Columna 'ticket' agregada a la tabla 'pedidos' correctamente.")
except Exception as e:
    print(f"Error: {e}")
