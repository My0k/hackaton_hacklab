FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar primero los archivos de requisitos para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiar el resto de los archivos de la aplicación
COPY . .

# Ejecutar el script de configuración
RUN chmod +x setup.sh
RUN ./setup.sh

# Asegurar permisos para directorios importantes
RUN chmod -R 755 static templates
RUN chmod -R 777 static/fotos temp
RUN chmod 666 *.csv || true

# Exponer el puerto que utilizará la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación con gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"] 