#!/bin/bash

# Activar entorno virtual
source .venv/bin/activate

# Configurar variables de entorno
export OPENAI_API_KEY="dummy_key"

# Ejecutar todas las pruebas
python run_all_tests.py
