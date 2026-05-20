import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infra.db.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE compras_clientes ADD COLUMN IF NOT EXISTS monto_efectivo DECIMAL(10,2) DEFAULT 0.0;"))
        conn.execute(text("ALTER TABLE compras_clientes ADD COLUMN IF NOT EXISTS monto_yape DECIMAL(10,2) DEFAULT 0.0;"))
        conn.execute(text("ALTER TABLE compras_clientes ADD COLUMN IF NOT EXISTS monto_tarjeta DECIMAL(10,2) DEFAULT 0.0;"))
        conn.commit()
    print("Columnas de montos mixtos agregadas a la tabla 'compras_clientes' correctamente.")
except Exception as e:
    print(f"Error: {e}")
