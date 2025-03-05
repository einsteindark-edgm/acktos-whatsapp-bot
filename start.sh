#!/bin/bash

# Verificar si el entorno virtual existe y activarlo
if [ -d ".venv" ]; then
    echo "Activando entorno virtual..."
    source .venv/bin/activate
else
    echo "Creando entorno virtual..."
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Verificar si el archivo .env existe
if [ ! -f ".env" ]; then
    echo "Archivo .env no encontrado. Copiando de .env.example..."
    cp .env.example .env
    echo "Por favor, edita el archivo .env con tus valores reales antes de continuar."
    exit 1
fi

# Ejecutar la aplicación con uvicorn
echo "Iniciando la aplicación..."
uvicorn main:app --reload --port 8000
