import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel
from models.dependencies import VisionAgentDependencies

class VisionResult(BaseModel):
    """Resultado del procesamiento de visión"""
    extracted_text: str = Field(description="Texto extraído de la imagen")
    confidence: float = Field(description="Nivel de confianza en la extracción", ge=0, le=1)
    provider: str = Field(description="Proveedor utilizado para la extracción")
    model: str = Field(description="Modelo utilizado para la extracción")

# Determinar el modelo a usar según el entorno
def get_model_for_environment():
    # Si estamos en un entorno de prueba, usamos TestModel
    if os.environ.get('PYDANTICAI_ALLOW_MODEL_REQUESTS', 'true').lower() == 'false':
        print("VisionAgent: Usando TestModel para pruebas")
        return TestModel()
    # Si no, usamos un modelo OpenAI con capacidades de visión
    # gpt-4o es el modelo actual con capacidades de visión
    print("VisionAgent: Utilizando modelo OpenAI gpt-4o")
    return 'openai:gpt-4o'

vision_agent = Agent(
    get_model_for_environment(),
    deps_type=VisionAgentDependencies,
    result_type=VisionResult,
    system_prompt=(
        "Eres un agente especializado en extraer información de imágenes de facturas. "
        "Tu objetivo es identificar y extraer toda la información relevante de la factura "
        "incluyendo número de factura, fecha, vendedor, items, montos y cualquier otro dato importante."
    )
)

@vision_agent.tool
async def process_invoice_image(
    ctx: RunContext[VisionAgentDependencies]
) -> VisionResult:
    """
    Procesa una imagen de factura y extrae su contenido.
    
    Args:
        ctx: Contexto de ejecución con dependencias que incluye la imagen
        
    Returns:
        VisionResult: Resultado del procesamiento de la imagen
    """
    # Obtener la imagen de las dependencias
    if not ctx.deps.image_data:
        raise ValueError("No se proporcionó imagen para procesar")
    
    # Agregar logs detallados para depuración
    print(f"VisionAgent: Procesando imagen de {len(ctx.deps.image_data)} bytes")
    print(f"VisionAgent: Usando modelo {ctx.deps.model_name}")
    print(f"VisionAgent: API key configurada: {bool(ctx.deps.api_key)}")
        
    result = await ctx.deps.vision_provider.process_image(
        image_data=ctx.deps.image_data,
        model_name=ctx.deps.model_name,
        api_key=ctx.deps.api_key
    )
    
    # Log del resultado
    print(f"VisionAgent: Texto extraído: {len(result['extracted_text'])} caracteres")
    
    return VisionResult(
        extracted_text=result["extracted_text"],
        confidence=0.95,  # Este valor debería venir del proveedor
        provider=result["provider"],
        model=result["model"]
    )
