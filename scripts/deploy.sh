#!/bin/bash

set -e  # Detener en caso de error

echo "Iniciando despliegue del servicio WhatsApp Invoice Processor..."

# Verificar si Docker está instalado
if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: Docker no está instalado.' >&2
  exit 1
fi

# Verificar si docker-compose está instalado
if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: Docker Compose no está instalado.' >&2
  exit 1
fi

# Verificar existencia del archivo .env
if [ ! -f ".env" ]; then
  echo 'Error: Archivo .env no encontrado. Por favor, crea este archivo basado en .env.example' >&2
  exit 1
fi

# Construir y levantar los contenedores
echo "Construyendo y desplegando contenedores Docker..."
docker-compose build --no-cache
docker-compose up -d

echo "Verificando estado de los contenedores..."
docker-compose ps

echo "Mostrando logs iniciales..."
docker-compose logs -f --tail=20

echo "Despliegue completado con éxito!"
echo "La aplicación está disponible en: http://localhost:8000"
echo "Para verificar el estado de la aplicación, visita: http://localhost:8000/health"
echo "Para ver los logs: docker-compose logs -f"
