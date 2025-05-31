FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorio .well-known y el archivo de verificación
RUN mkdir -p .well-known
RUN echo "OK" > .well-known/captain-identifier

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "4", "app:app"] 