#!/bin/bash

set -e  # Detener en caso de error

echo "Configurando entorno de desarrollo para WhatsApp Invoice Processor..."

# Verificar si Python 3.10+ estu00e1 instalado
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
  echo "Error: Se requiere Python 3.10 o superior (versiu00f3n actual: $PYTHON_VERSION)"
  exit 1
fi

echo "Python versiu00f3n $PYTHON_VERSION detectado. Continuando..."

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
  echo "Creando entorno virtual..."
  python3 -m venv .venv
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source .venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Verificar archivo .env
if [ ! -f ".env" ]; then
  echo "Creando archivo .env de ejemplo..."
  cp .env.example .env
  echo "IMPORTANTE: Edita el archivo .env con tus credenciales y configuraciones"
fi

echo ""
echo "Configuraciu00f3n completada exitosamente!"
echo ""
echo "Para iniciar el servidor de desarrollo:"
echo "  $ source .venv/bin/activate  # Si au00fan no estu00e1 activado"
echo "  $ ./start.sh"
echo ""
echo "Para ejecutar pruebas:"
echo "  $ ./test_fastapi.sh"
echo ""
echo "Para probar webhooks localmente:"
echo "  1. Inicia el servidor de desarrollo"
echo "  2. En otra terminal, ejecuta: $ ./test_webhook.sh"
echo "  3. Para exponer tu servidor local, usa ngrok: $ ngrok http 8000"
echo ""
echo "Feliz desarrollo!"
