import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

# Au00f1adir el directorio rau00edz del proyecto al PATH de Python
root_dir = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, root_dir)

# Configurar variables de entorno necesarias
os.environ['OPENAI_API_KEY'] = 'dummy_key'

# Desactivar llamadas reales a modelos
from pydantic_ai import models
from pydantic_ai import capture_run_messages
models.ALLOW_MODEL_REQUESTS = False

# Importar TestModel
from pydantic_ai.models.test import TestModel

# Importar agentes y dependencias
from agents.vision_agent import vision_agent, VisionResult
from models.dependencies import VisionAgentDependencies
from tests.unit.mocks.providers import MockVisionProvider

# Datos de imagen simulados
dummy_image_data = b"dummy_image_data"

# Respuesta simulada para el proceso_invoice_image
expected_result = VisionResult(
    extracted_text="FACTURA\nNu00famero: INV-001\nFecha: 2023-01-15\nVendedor: Test Company\nCliente: Test Client\nItems:\n1. Producto A - $100.00\nImpuestos: $19.00\nTotal: $119.00 USD",
    confidence=0.95,
    provider="mock_provider",
    model="gpt-4-vision"
)


async def test_vision_agent():
    """Prueba del agente de visiu00f3n"""
    print("Ejecutando prueba del agente de vision...\n")
    
    # Crear dependencias mock
    deps = VisionAgentDependencies(
        vision_provider=MockVisionProvider(),
        model_name="gpt-4-vision",
        api_key="dummy_key"
    )
    
    # Usar TestModel para simular respuestas del modelo con resultados predefinidos
    with vision_agent.override(model=TestModel(custom_result_args=expected_result)), capture_run_messages() as msgs:
        # Ejecutar el agente con la imagen de prueba usando la misma forma que en el test de integración
        # Nota: No se especifica el nombre de la herramienta, solo se pasa la imagen como primer argumento
        result = await vision_agent.run(dummy_image_data, deps=deps)
    
    # Verificar resultado
    success = True
    
    # Verificar que el resultado tenga la estructura esperada
    if not (result and hasattr(result, 'data')):
        print(f"[FAIL] Estructura de resultado incorrecta: {result}")
        return False
    
    # Obtener los datos del resultado
    vision_data = result.data
    
    # Verificar texto extraído
    if "FACTURA" in vision_data.extracted_text and "INV-001" in vision_data.extracted_text:
        print("[PASS] Resultado correcto: FACTURA\nNumero: INV-001\nFecha:...")
    else:
        print(f"[FAIL] Texto extraído incorrecto: {vision_data.extracted_text if hasattr(vision_data, 'extracted_text') else 'No extracted_text attribute'}")
        success = False
    
    # Verificar proveedor
    if hasattr(vision_data, 'provider') and vision_data.provider == "mock_provider":
        print("[PASS] Proveedor: mock_provider")
    else:
        print(f"[FAIL] Proveedor incorrecto: {vision_data.provider if hasattr(vision_data, 'provider') else 'No provider attribute'}")
        success = False
    
    # Verificar modelo
    if hasattr(vision_data, 'model') and vision_data.model == "gpt-4-vision":
        print("[PASS] Modelo: gpt-4-vision")
    else:
        print(f"[FAIL] Modelo incorrecto: {vision_data.model if hasattr(vision_data, 'model') else 'No model attribute'}")
        success = False
    
    # Verificar confianza
    if hasattr(vision_data, 'confidence') and vision_data.confidence > 0.5:
        print(f"[PASS] Confianza: {vision_data.confidence}")
    else:
        print(f"[FAIL] Confianza demasiado baja: {vision_data.confidence if hasattr(vision_data, 'confidence') else 'No confidence attribute'}")
        success = False
    
    print("\n[PASS] La prueba del agente de vision paso correctamente!" if success else "\n[FAIL] La prueba del agente de vision fallo!")
    
    return 0 if success else 1


async def main():
    """Funciu00f3n principal"""
    # Ejecutar la prueba del agente de visiu00f3n
    vision_result = await test_vision_agent()
    
    # Determinar el estado general
    if vision_result == 0:
        return 0  # u00c9xito
    else:
        return 1  # Fallo


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
