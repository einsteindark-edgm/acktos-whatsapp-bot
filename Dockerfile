FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el cu00f3digo fuente
COPY . .

# Variables de entorno por defecto
ENV PORT=8000
ENV ENVIRONMENT=production

# Exponer puerto
EXPOSE ${PORT}

# Comando para iniciar la aplicaciu00f3n
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
