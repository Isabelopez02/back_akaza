# ==========================================================
# 🐳 AKAZA FastAPI Backend - Dockerfile de Producción
# ==========================================================

# 1. Usar una imagen oficial de Python ligera como base
FROM python:3.11-slim as base

# 2. Configurar variables de entorno optimizadas para Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# 3. Establecer el directorio de trabajo del contenedor
WORKDIR /app

# 4. Instalar dependencias esenciales del sistema operativo
# - build-essential y libpq-dev: Necesarios para compilar paquetes de Python como psycopg2
# - curl: Excelente para realizar comprobaciones de salud del contenedor (Health Checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiar los archivos de requerimientos primero para aprovechar la memoria caché de Docker
COPY requirements.txt .

# 6. Instalar y actualizar pip y las dependencias del proyecto
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 7. Copiar la totalidad del código del backend al contenedor
COPY . .

# 8. Exponer el puerto estándar en el que correrá la aplicación FastAPI
EXPOSE 8000

# 9. Comando de arranque de producción usando Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
