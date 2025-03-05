import pytest
from pydanticai import models
from pydanticai.testing import TestModel, capture_run_messages

# Marcar todas las pruebas como asu00edncronas
pytestmark = pytest.mark.anyio

# Evitar llamadas reales a modelos durante las pruebas
models.ALLOW_MODEL_REQUESTS = False

# Importar despuu00e9s para evitar problemas con ALLOW_MODEL_REQUESTS
from agents.vision_agent import vision_agent, VisionAgentDependencies, VisionAgentResult


@pytest.fixture
def mock_dependencies():
    """Mock de dependencias para el vision_agent"""
    class MockVisionProvider:
        async def extract_text_from_image(self, image_url):
            # Texto simulado de una factura
            return """FACTURA\nNu00b0: A-12345\nFecha: 15/07/2023\nProveedor: ACME Servicios, S.A.\nCIF: B-12345678\nCliente: Empresa Cliente SL\nCIF: B-87654321\nConcepto: Servicios de consultoriu00eda\nBase imponible: 1.000,00 EUR\nIVA (21%): 210,00 EUR\nTotal: 1.210,00 EUR"""
    
    return VisionAgentDependencies(
        vision_provider=MockVisionProvider()
    )


async def test_vision_agent_extract_text():
    """Prueba que el agente de visiu00f3n extraiga correctamente el texto de una imagen"""
    # Capturar mensajes para verificaciu00f3n
    with capture_run_messages() as messages:
        # Usar TestModel para simular respuestas del LLM
        with vision_agent.override(model=TestModel()):
            # Ejecutar el agente
            result = await vision_agent.run(
                "Extraer texto de esta factura", 
                deps=mock_dependencies(), 
                context={"image_url": "https://example.com/invoice.jpg"}
            )
    
    # Verificar que el resultado sea del tipo esperado
    assert isinstance(result, VisionAgentResult)
    # Verificar que contenga texto extrau00eddo
    assert "FACTURA" in result.extracted_text
    assert "1.210,00 EUR" in result.extracted_text
    
    # Opcional: Verificar que se invocaron las herramientas adecuadas
    tool_calls = [msg for msg in messages if msg.get("role") == "assistant" and msg.get("tool_calls")]
    assert len(tool_calls) > 0, "El agente deberu00eda usar al menos una herramienta"


async def test_vision_agent_handles_empty_image():
    """Prueba que el agente maneje adecuadamente imu00e1genes sin texto"""
    # Crear un mock que simule una imagen sin texto
    class EmptyImageMockProvider:
        async def extract_text_from_image(self, image_url):
            return ""
    
    deps = VisionAgentDependencies(vision_provider=EmptyImageMockProvider())
    
    # Usar TestModel para simular respuestas del LLM
    with vision_agent.override(model=TestModel()):
        # Ejecutar el agente
        result = await vision_agent.run(
            "Extraer texto de esta imagen", 
            deps=deps, 
            context={"image_url": "https://example.com/empty.jpg"}
        )
    
    # Verificar manejo de caso sin texto
    assert result.extracted_text == ""
    assert not result.success
    assert "No se pudo extraer" in result.error_message
