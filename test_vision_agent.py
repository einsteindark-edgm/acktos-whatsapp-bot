import os
import sys
import asyncio
from typing import Dict, Any, List, Optional

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
    extracted_text="FACTURA\nNumero: INV-001\nFecha: 17/02/2024\nVendedor: Test Company\nNIT: 123456789\n\nItem 1 - 100.00 x 1 = 100.00\n\nSubtotal: 100.00\nIVA: 19.00\nTotal: 119.00 USD",
    confidence=0.95,
    provider="mock_provider",
    model="gpt-4-vision"
)

async def test_vision_agent():
    print("\nPrueba del agente de vision...")
    
    try:
        # Configurar dependencias
        vision_provider = MockVisionProvider()
        deps = VisionAgentDependencies(
            vision_provider=vision_provider,
            model_name="gpt-4-vision",
            api_key="valid-key"
        )
        
        # Crear respuesta para el MockVisionProvider
        mock_provider_response = {
            "extracted_text": expected_result.extracted_text,
            "provider": expected_result.provider,
            "model": expected_result.model
        }
        
        # Configurar el mock para que devuelva nuestra respuesta simulada
        async def mock_process_image(*args, **kwargs):
            return mock_provider_response
        
        # Reemplazar el método original con nuestro mock
        vision_provider.process_image = mock_process_image
        
        # Ejecutar el agente con TestModel y capturar mensajes
        with capture_run_messages() as messages:
            with vision_agent.override(model=TestModel(custom_result_args=expected_result)):
                result = await vision_agent.run(dummy_image_data, deps=deps)

        # Verificar resultado
        if result and hasattr(result, 'data') and isinstance(result.data, VisionResult):
            vision_result = result.data
            print(f"[PASS] Resultado correcto: {vision_result.extracted_text[:30]}...")
            print(f"[PASS] Proveedor: {vision_result.provider}")
            print(f"[PASS] Modelo: {vision_result.model}")
            print(f"[PASS] Confianza: {vision_result.confidence}")
            
            # Verificar que el resultado coincide con lo esperado
            assert vision_result.extracted_text == expected_result.extracted_text
            assert vision_result.provider == expected_result.provider
            assert vision_result.model == expected_result.model
            assert vision_result.confidence == expected_result.confidence
            
            return True
        else:
            print(f"[FAIL] Resultado incorrecto: {result}")
            return False
    except Exception as e:
        print(f"[FAIL] Error en la prueba del agente de vision: {e}")
        return False

async def main():
    print("Ejecutando prueba del agente de vision...")
    
    # Ejecutar prueba
    success = await test_vision_agent()
    
    if success:
        print("\n[PASS] La prueba del agente de vision paso correctamente!")
        return 0
    else:
        print("\n[FAIL] La prueba del agente de vision fallo!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar la prueba: {e}")
        sys.exit(1)
