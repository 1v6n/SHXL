# Dockerfile
# filepath: /home/ivan/Visual Studio Projects/SHXL/backend/Dockerfile

# Usar imagen base de Python
FROM python:3.12-slim-bullseye

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/

# Exponer puerto
EXPOSE 5000

# Establecer variables de entorno
ENV FLASK_APP=src.api.app
ENV FLASK_ENV=development
ENV PYTHONPATH=/app

# Comando para ejecutar la aplicación
CMD ["python", "-m", "src.api.app"]
