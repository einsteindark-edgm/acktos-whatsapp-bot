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

# Marcar todas las pruebas como asíncronas
pytestmark = pytest.mark.anyio

# Evitar llamadas reales a modelos durante las pruebas
models.ALLOW_MODEL_REQUESTS = False

# Importar después para evitar problemas con ALLOW_MODEL_REQUESTS
from agents.vision_agent import vision_agent, VisionResult  # Nombre correcto de la clase
from models.dependencies import VisionAgentDependencies  # Importar desde la ubicación correcta


@pytest.fixture
def mock_dependencies():
    """Mock de dependencias para el vision_agent"""
    class MockVisionProvider:
        async def extract_text_from_image(self, image_url):
            # Texto simulado de una factura
            return """FACTURA
N°: A-12345
Fecha: 15/07/2023
Proveedor: ACME Servicios, S.A.
CIF: B-12345678
Cliente: Empresa Cliente SL
CIF: B-87654321
Concepto: Servicios de consultoría
Base imponible: 1.000,00 EUR
IVA (21%): 210,00 EUR
Total: 1.210,00 EUR"""
    
    return VisionAgentDependencies(
        vision_provider=MockVisionProvider(),
        model_name="gpt-4-vision",
        api_key="dummy_key"
    )


async def test_vision_agent_extract_text():
    """Prueba que el agente de visión extraiga correctamente el texto de una imagen"""
    # Capturar mensajes para verificación
    with capture_run_messages() as messages:
        # Usar TestModel para simular respuestas del modelo
        with vision_agent.override(model=TestModel()):
            # Mock de dependencias
            deps = mock_dependencies()
            # Datos de imagen simulados
            image_data = b"fake_image_data"
            # Llamar al agente
            result = await vision_agent.process_invoice_image(image_data, deps=deps)
    
    # Verificar resultado
    assert isinstance(result, VisionResult)
    assert "FACTURA" in result.extracted_text
    assert "A-12345" in result.extracted_text
    assert result.provider == "mock_provider"  # Asumiendo que el provider mock tiene este nombre
    assert result.model == "gpt-4-vision"
    assert result.confidence > 0.5  # Asumiendo un nivel de confianza razonable


async def test_vision_agent_handles_empty_image():
    """Prueba que el agente maneje adecuadamente imágenes sin texto"""
    # Capturar mensajes para verificación
    with capture_run_messages() as messages:
        # Usar TestModel para simular respuestas del modelo
        with vision_agent.override(model=TestModel()):
            # Mock de dependencias con proveedor que devuelve texto vacío
            class EmptyImageMockProvider:
                async def extract_text_from_image(self, image_url):
                    return ""
            
            deps = VisionAgentDependencies(
                vision_provider=EmptyImageMockProvider(),
                model_name="gpt-4-vision",
                api_key="dummy_key"
            )
            
            # Datos de imagen simulados
            image_data = b"empty_image_data"
            # Llamar al agente
            result = await vision_agent.process_invoice_image(image_data, deps=deps)
    
    # Verificar resultado para imagen vacía
    assert isinstance(result, VisionResult)
    assert result.extracted_text == ""
    assert result.confidence < 0.5  # Confianza baja para imagen sin texto
