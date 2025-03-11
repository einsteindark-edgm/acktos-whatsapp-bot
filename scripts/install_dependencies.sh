#!/bin/bash

# Script para instalar dependencias de forma controlada
set -e

echo "===== Instalando dependencias básicas ====="
python -m pip install --upgrade pip setuptools wheel

echo "===== Instalando dependencias de testing ====="
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-html

echo "===== Instalando dependencias principales ====="
pip install fastapi==0.110.0 uvicorn[standard]==0.27.1
pip install pydantic==2.10.6 pydantic-settings==2.1.0
pip install python-dotenv==1.0.0 python-multipart==0.0.9

echo "===== Instalando bibliotecas de bases de datos y Azure ====="
pip install pymongo==4.6.1
pip install azure-functions==1.17.0

echo "===== Instalando OpenAI ====="
pip install openai==1.12.0

echo "===== Verificando si OpenAI se instaló correctamente ====="
pip show openai

echo "===== Instalando pydantic-ai con soporte para OpenAI ====="
pip uninstall -y pydantic-ai pydantic-ai-slim || true
pip install 'pydantic-ai[openai]==0.0.30' || pip install 'pydantic-ai-slim[openai]==0.0.30'

echo "===== Verificando instalación de pydantic-ai ====="
pip show pydantic-ai || pip show pydantic-ai-slim

echo "===== Instalando utilidades y bibliotecas de red ====="
pip install httpx==0.27.0 requests==2.31.0 aiohttp==3.9.3
pip install typing_extensions==4.12.2 certifi==2024.8.30

echo "===== Lista completa de dependencias instaladas ====="
pip list
