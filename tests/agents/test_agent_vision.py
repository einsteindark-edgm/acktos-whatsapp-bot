import os
import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al PATH de Python
root_dir = Path(__file__).parent.parent.parent.absolute()
print(f"Añadiendo directorio raíz al PATH: {root_dir}")
sys.path.insert(0, str(root_dir))

import pytest
from pydantic_ai import models, capture_run_messages
from pydantic_ai.models.test import TestModel

# Usar asyncio exclusivamente, sin parametrización para evitar problemas con trio
# Esto es crucial para que los tests funcionen en CI donde trio no está instalado
pytestmark = pytest.mark.asyncio  # Usar pytest.mark.asyncio en lugar de anyio

# Evitar llamadas reales a modelos durante las pruebas
models.ALLOW_MODEL_REQUESTS = False

# Importar después para evitar problemas con ALLOW_MODEL_REQUESTS
from agents.vision_agent import vision_agent, VisionResult  # Nombre correcto de la clase
from models.dependencies import VisionAgentDependencies  # Importar desde la ubicación correcta


@pytest.fixture
def mock_dependencies():
    """Mock de dependencias para el vision_agent"""
    class MockVisionProvider:
        async def process_image(self, image_data, model_name, api_key):
            # Texto simulado de una factura
            return {
                "extracted_text": """FACTURA
N°: A-12345
Fecha: 15/07/2023
Proveedor: ACME Servicios, S.A.
CIF: B-12345678
Cliente: Empresa Cliente SL
CIF: B-87654321
Concepto: Servicios de consultoría
Base imponible: 1.000,00 EUR
IVA (21%): 210,00 EUR
Total: 1.210,00 EUR""",
                "provider": "mock_provider",
                "model": model_name,
                "confidence": 0.9
            }
    
    return VisionAgentDependencies(
        vision_provider=MockVisionProvider(),
        model_name="gpt-4-vision",
        api_key="dummy_key"
    )


async def test_vision_agent_extract_text(mock_dependencies):
    """Prueba que el agente de visión extraiga correctamente el texto de una imagen"""
    # Capturar mensajes para verificación
    with capture_run_messages() as messages:
        # Crear los resultados esperados para el TestModel
        expected_result = VisionResult(
            extracted_text="""FACTURA
N°: A-12345
Fecha: 15/07/2023
Proveedor: ACME Servicios, S.A.
CIF: B-12345678
Cliente: Empresa Cliente SL
CIF: B-87654321
Concepto: Servicios de consultoría
Base imponible: 1.000,00 EUR
IVA (21%): 210,00 EUR
Total: 1.210,00 EUR""",
            provider="mock_provider",
            model="gpt-4-vision",
            confidence=0.9
        )
        
        # Usar TestModel para simular respuestas del modelo con resultados predefinidos
        with vision_agent.override(model=TestModel(custom_result_args=expected_result)):
            # Usar las dependencias pasadas como parámetro
            deps = mock_dependencies
            # Datos de imagen simulados
            image_data = b"fake_image_data"
            # Llamar al agente con .run() como en el test manual
            result = await vision_agent.run(image_data, deps=deps)
    
    # Verificar resultado (accediendo a través de result.data como en el test manual)
    assert result and hasattr(result, 'data')
    vision_data = result.data
    assert isinstance(vision_data, VisionResult)
    assert "FACTURA" in vision_data.extracted_text
    assert "A-12345" in vision_data.extracted_text
    assert vision_data.provider == "mock_provider"  # Asumiendo que el provider mock tiene este nombre
    assert vision_data.model == "gpt-4-vision"
    assert vision_data.confidence > 0.5  # Asumiendo un nivel de confianza razonable


async def test_vision_agent_handles_empty_image():
    """Prueba que el agente maneje adecuadamente imágenes sin texto"""
    # Capturar mensajes para verificación
    with capture_run_messages() as messages:
        # Crear los resultados esperados para el TestModel (imagen vacía)
        expected_empty_result = VisionResult(
            extracted_text="",
            provider="mock_provider",
            model="gpt-4-vision",
            confidence=0.1
        )
        
        # Usar TestModel para simular respuestas del modelo con resultados predefinidos
        with vision_agent.override(model=TestModel(custom_result_args=expected_empty_result)):
            # Mock de dependencias con proveedor que devuelve texto vacío
            class EmptyImageMockProvider:
                async def process_image(self, image_data, model_name, api_key):
                    return {
                        "extracted_text": "",
                        "provider": "mock_provider",
                        "model": model_name,
                        "confidence": 0.1
                    }
            
            deps = VisionAgentDependencies(
                vision_provider=EmptyImageMockProvider(),
                model_name="gpt-4-vision",
                api_key="dummy_key"
            )
            
            # Datos de imagen simulados
            image_data = b"empty_image_data"
            # Llamar al agente con .run()
            result = await vision_agent.run(image_data, deps=deps)
    
    # Verificar resultado para imagen vacía (accediendo a través de result.data)
    assert result and hasattr(result, 'data')
    vision_data = result.data
    assert isinstance(vision_data, VisionResult)
    assert vision_data.extracted_text == ""
    assert vision_data.confidence < 0.5  # Confianza baja para imagen sin texto
