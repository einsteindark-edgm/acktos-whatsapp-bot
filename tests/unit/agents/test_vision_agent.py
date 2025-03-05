import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic_ai import models, capture_run_messages
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    ModelRequest,
    AgentInfo
)

from agents.vision_agent import vision_agent, VisionResult
from models.dependencies import VisionAgentDependencies
from providers.vision.base import VisionProvider

pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False  # Prevenir llamadas reales al API


from tests.unit.mocks.providers import MockVisionProvider


async def test_process_invoice_image_with_testmodel(vision_deps, message_capture, override_vision_agent):
    """Test para verificar que el agente puede procesar imágenes de facturas usando TestModel."""
    # Datos de imagen simulados
    image_data = b"fake_image_data"
    
    # Ejecutar la herramienta directamente
    result = await vision_agent.tools.process_invoice_image(
        image_data=image_data,
        deps=vision_deps
    )
    
    # Verificar que el resultado es una instancia de VisionResult
    assert isinstance(result, VisionResult)
    assert result.provider == "mock_provider"
    assert result.model == "test-model"
    assert "FACTURA" in result.extracted_text


def call_vision_agent(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """Función personalizada para FunctionModel que simula respuestas específicas."""
    # Primera llamada: llamar a la herramienta process_invoice_image
    if len(messages) == 1:
        return ModelResponse(parts=[
            ToolCallPart(
                tool_name='process_invoice_image',
                args={'image_data': b'custom_image_data'}
            )
        ])
    # Segunda llamada: devolver un resultado personalizado
    else:
        return ModelResponse(parts=[
            TextPart(content='{"extracted_text": "Texto personalizado", "confidence": 0.99, "provider": "custom", "model": "custom-model"}')
        ])


async def test_process_invoice_image_with_functionmodel():
    """Test para verificar que el agente puede procesar imágenes usando FunctionModel."""
    # Crear dependencias con proveedor simulado
    mock_provider = MockVisionProvider()
    deps = VisionAgentDependencies(
        vision_provider=mock_provider,
        model_name="test-model",
        api_key="test-key"
    )
    
    # Capturar mensajes durante la ejecución
    with capture_run_messages() as messages:
        # Usar FunctionModel para controlar exactamente el comportamiento
        with vision_agent.override(model=FunctionModel(call_vision_agent)):
            # Ejecutar el agente
            result = await vision_agent.run("Procesa esta imagen de factura", deps=deps)
    
    # Verificar que el resultado contiene los datos personalizados
    assert result.data.confidence == 0.99
    assert result.data.provider == "custom"
    assert result.data.model == "custom-model"
    assert result.data.extracted_text == "Texto personalizado"
