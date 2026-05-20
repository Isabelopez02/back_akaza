import os
import sys

# Agregar el directorio actual al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infra.db.database import engine, Base
from infra.db.models import __init__  # Importa los modelos

print("Creando tablas faltantes...")
Base.metadata.create_all(bind=engine)
print("¡Tablas creadas/verificadas con éxito!")
