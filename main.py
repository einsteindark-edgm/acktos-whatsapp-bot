import os
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Cargar variables de entorno explícitamente
load_dotenv()

# Verificar que la clave de API esté cargada
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"API Key cargada correctamente: {api_key[:10]}...{api_key[-4:]}")
else:
    print("ADVERTENCIA: No se encontró la variable OPENAI_API_KEY")

from app.routers import webhook
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de recursos necesarios
    print(f"Iniciando aplicación en ambiente: {settings.ENVIRONMENT}")
    yield
    # Limpieza al cerrar la aplicación
    print("Cerrando la aplicación")

# Crear la aplicación FastAPI
app = FastAPI(
    title="WhatsApp Invoice Processor",
    description="Servicio para procesar facturas a través de WhatsApp",
    version="1.0.0",
    lifespan=lifespan
)

# Incluir routers
# Agregar prefijo /api para mantener consistencia con Azure Functions
app.include_router(webhook.router, prefix="/api")

# Ruta de estado/health-check
@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8000")),
        reload=settings.ENVIRONMENT == "development"
    )
