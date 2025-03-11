#!/bin/bash

# Activar entorno virtual
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Entorno virtual no encontrado. Ejecuta primero start.sh para configurarlo."
    exit 1
fi

# Ejecutar pruebas FastAPI con pytest
echo "Ejecutando pruebas de FastAPI..."
pytest tests/app -v
