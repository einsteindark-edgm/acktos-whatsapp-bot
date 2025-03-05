#!/bin/bash

set -e  # Detener en caso de error

echo "Ejecutando pruebas de los agentes PydanticAI..."

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Establecer variable para evitar llamadas reales a OpenAI
export PYDANTICAI_ALLOW_MODEL_REQUESTS=false

# Ejecutar pruebas especu00edficas de los agentes
pytest -xvs tests/agents/ $@

echo "Pruebas de agentes completadas."

# Si se pasa -c como argumento, ejecutar pruebas de cobertura
if [[ " $* " == *" -c "* ]]; then
  echo "Generando informe de cobertura para los agentes..."
  python -m pytest --cov=agents tests/agents/ --cov-report=term --cov-report=html:cov_html
  echo "Informe de cobertura generado en: ./cov_html"
fi
