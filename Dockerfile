# ==========================================================
# 🐳 AKAZA FastAPI Backend - Dockerfile de Producción
# ==========================================================

# ── Etapa 1: Builder (Compilación de dependencias) ────────
FROM python:3.11-slim AS builder

# Evitar escritura de archivos .pyc y forzar salida de logs sin búfer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Instalar herramientas esenciales del SO para compilar paquetes (ej. psycopg2, cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear entorno virtual aislado
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar requirements e instalar dependencias en el venv sin caché
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ── Etapa 2: Runner (Imagen final ligera y segura) ───────
FROM python:3.11-slim AS runner

# Configuración de entorno para producción
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000 \
    WORKERS=2

WORKDIR /app

# Instalar únicamente librerías de ejecución en runtime y curl para health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual con todas las dependencias ya compiladas desde el builder
COPY --from=builder /opt/venv /opt/venv

# Crear usuario y grupo no-root para máxima seguridad en producción
RUN groupadd -g 1001 akaza && \
    useradd -u 1001 -g akaza -s /bin/sh -m akaza

# Copiar el código fuente con permisos para el usuario akaza
COPY --chown=akaza:akaza . /app

# Cambiar al usuario sin privilegios
USER akaza

# Exponer el puerto predeterminado
EXPOSE 8000

# Verificación de salud (Health Check)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

# Comando de inicio: soporta asignación dinámica de puerto ($PORT) y workers ($WORKERS)
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-2}"]
