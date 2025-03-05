# WhatsApp Invoice Processor

Servicio para procesar facturas a través de WhatsApp utilizando PydanticAI para crear agentes inteligentes que extraen información de imágenes.

## Características

- Procesamiento de imágenes de facturas usando OpenAI Vision
- Extracción de datos estructurados
- Almacenamiento en CosmosDB
- Respuestas rápidas a través de WhatsApp
- Arquitectura modular basada en agentes PydanticAI

## Requisitos

- Python 3.10+
- Cuenta de WhatsApp Business API
- API Key de OpenAI
- Base de datos compatible con MongoDB (ej: Azure CosmosDB)

## Estructura del Proyecto

```
└── whatsapp-driver-service/
    ├── app/                  # Directorio principal de la aplicación
    │   ├── config.py         # Configuración y variables de entorno
    │   ├── dependencies.py   # Dependencias para inyección
    │   └── routers/          # Endpoints API
    │       └── webhook.py    # Manejo de webhooks de WhatsApp
    ├── agents/               # Agentes de IA
    ├── models/               # Modelos de datos
    ├── providers/            # Proveedores de servicios
    │   ├── storage/          # Proveedores de almacenamiento
    │   └── vision/           # Proveedores de visión
    ├── scripts/              # Scripts de despliegue y utilidades
    ├── tests/                # Pruebas
    ├── Dockerfile            # Definición para construir imagen Docker
    ├── docker-compose.yml    # Configuración para despliegue con Docker Compose
    ├── main.py               # Punto de entrada de la aplicación
    ├── requirements.txt      # Dependencias Python
    ├── start.sh              # Script para iniciar el servidor
    └── utils.py              # Funciones auxiliares
```

## Desarrollo Local

### Configuración Rápida

```bash
./scripts/setup_dev.sh
```

Este script configurará automáticamente el entorno de desarrollo para ti, incluyendo la creación del entorno virtual, la instalación de dependencias y la configuración inicial.

### Configuración Manual

1. Clonar el repositorio y navegar a la carpeta del proyecto

2. Crear y activar entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows usa `.venv\Scripts\activate`
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar el archivo .env con tus claves y configuraciones
```

5. Iniciar la aplicación:
```bash
./start.sh  # Alternativa: uvicorn main:app --reload
```

6. Acceder a la documentación de la API:
```
http://localhost:8000/docs
```

## Pruebas con ngrok

Para probar la integración con WhatsApp, puedes usar ngrok para exponer tu servidor local:

1. Instalar ngrok: https://ngrok.com/download

2. Iniciar un túnel HTTP en el puerto 8000:
```bash
ngrok http 8000
```

3. Copiar la URL HTTPS generada por ngrok (ej: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app`)

4. Configurarla en el panel de desarrollador de WhatsApp:
   - URL del Webhook: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/webhook`
   - Usar el token de verificación definido en tu archivo .env

## Endpoints API

### GET /webhook

Verificación del webhook de WhatsApp.

Query Parameters:
- `hub.mode`: Debe ser 'subscribe'
- `hub.verify_token`: Token de verificación definido en tu configuración
- `hub.challenge`: Challenge string que se devolverá como respuesta

### POST /webhook

Recibe mensajes de WhatsApp y procesa imágenes de facturas.

### GET /health

Endpoint de health check que devuelve el estado de la aplicación.

## Despliegue

### Opciones de Despliegue

La aplicación puede desplegarse en cualquier plataforma que soporte Python y FastAPI:

- Heroku
- Google Cloud Run
- Render
- Railway
- Contenedor Docker personalizado (recomendado)

### Despliegue con Docker

#### Prerrequisitos

- Docker y Docker Compose instalados
- Archivo `.env` configurado con todas las variables necesarias

#### Despliegue Rápido

```bash
./scripts/deploy.sh
```

Este script verificará los prerrequisitos, construirá la imagen Docker y desplegará el servicio utilizando Docker Compose.

#### Despliegue Manual

1. Construir la imagen Docker: `docker-compose build`
2. Iniciar el servicio: `docker-compose up -d`
3. Verificar el estado: `docker-compose ps`
4. Ver logs: `docker-compose logs -f`

#### Verificación del Despliegue

Visita `http://localhost:8000/health` para verificar que el servicio está funcionando correctamente.
