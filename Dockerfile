FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar herramientas de compilación C/C++ y dependencias comunes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    cmake \
    pkg-config \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar sólo requirements para cachear la instalación
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copiar el resto de la app
COPY . /app

# Dar permisos de lectura/ejecución a posibles librerías nativas
RUN chmod -R a+rX /app/app/dll || true

EXPOSE 8000

# Ejecuta la app (producción: sin --reload)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
