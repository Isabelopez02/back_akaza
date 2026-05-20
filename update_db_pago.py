import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infra.db.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE compras_clientes ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(50) DEFAULT 'EFECTIVO';"))
        conn.commit()
    print("Columna 'metodo_pago' agregada a la tabla 'compras_clientes' correctamente.")
except Exception as e:
    print(f"Error: {e}")
