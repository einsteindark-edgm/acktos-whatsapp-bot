import pytest
import sys
import os
from datetime import datetime
from pydantic_ai import models, capture_run_messages
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel, AgentInfo
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
    ModelRequest,
)

from agents.data_extraction_agent import extraction_agent
from models.dependencies import ExtractorAgentDependencies
from models.invoice import Invoice, InvoiceItem
from tests.unit.mocks.providers import MockVisionProvider, MockStorageProvider

# Importar fixtures desde el nuevo archivo conftest_no_azure.py
pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False  # Prevenir llamadas reales al API
os.environ['OPENAI_API_KEY'] = 'dummy_key'  # Configurar una clave API ficticia


async def test_parse_invoice_text(extractor_deps, message_capture, override_extraction_agent):
    """Test para verificar que el agente puede analizar texto de factura correctamente."""
    # Texto de factura de ejemplo
    invoice_text = """
    FACTURA
    Número: INV-001
    Fecha: 17/02/2024
    
    Vendedor: Tech Solutions Inc
    NIT: 123456789
    
    Descripción                 Cantidad    Precio Unit.    Total
    Laptop Dell XPS 13         1           1000.00         1000.00
    
    Subtotal: 1000.00
    Impuestos: 150.00
    Total: 1150.00 USD
    """
    
    # Ejecutar el agente (el modelo ya está reemplazado por la fixture)
    result = await extraction_agent.run(invoice_text, deps=extractor_deps)
    
    # Verificar que el resultado es una instancia de Invoice
    assert isinstance(result.data, Invoice)
    
    # Verificar que los mensajes tienen la estructura esperada
    assert len(messages) >= 2  # Al menos request y response
    
    # Verificar que se llamó a la herramienta parse_invoice_text
    tool_call_found = False
    for message in messages:
        if isinstance(message, ModelResponse):
            for part in message.parts:
                if isinstance(part, ToolCallPart) and part.tool_name == 'parse_invoice_text':
                    tool_call_found = True
                    break
    
    assert tool_call_found, "No se encontró llamada a la herramienta parse_invoice_text"


async def test_validate_amounts(extractor_deps, message_capture, override_extraction_agent):
    """Test para verificar que el agente puede validar montos correctamente."""
    # Crear items de factura de ejemplo
    items = [
        InvoiceItem(description="Item 1", quantity=2, unit_price=100, total=200),
        InvoiceItem(description="Item 2", quantity=1, unit_price=300, total=300),
    ]
    
    # Montos correctos
    total_amount = 550  # 500 + 50 de impuestos
    tax_amount = 50
    
    # Ejecutar la herramienta directamente
    result = await extraction_agent.tools.validate_amounts(
        items=items,
        total_amount=total_amount,
        tax_amount=tax_amount,
        deps=extractor_deps
    )
    
    # Verificar que el resultado es True (montos válidos)
    assert result is True
    
    # Montos incorrectos
    total_amount_incorrect = 600  # No coincide con la suma
    
    # Limpiar mensajes capturados
    message_capture.clear()
    
    # Ejecutar la herramienta directamente con montos incorrectos
    result = await extraction_agent.tools.validate_amounts(
        items=items,
        total_amount=total_amount_incorrect,
        tax_amount=tax_amount,
        deps=extractor_deps
    )
    
    # Verificar que el resultado es False (montos inválidos)
    assert result is False


def call_extraction_agent(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """Función personalizada para FunctionModel que simula respuestas específicas."""
    # Primera llamada: llamar a la herramienta parse_invoice_text
    if len(messages) == 1:
        # Extraer el texto de la factura del mensaje del usuario
        user_prompt = messages[0].parts[-1].content
        return ModelResponse(parts=[
            ToolCallPart(
                tool_name='parse_invoice_text',
                args={'text': user_prompt}
            )
        ])
    # Segunda llamada: devolver una factura personalizada
    else:
        # Crear una factura de ejemplo como respuesta
        invoice = Invoice(
            invoice_number="FUNC-001",
            date=datetime.now(),
            vendor_name="FunctionModel Test",
            vendor_tax_id="123-456-789",
            total_amount=115.0,
            tax_amount=15.0,
            items=[
                InvoiceItem(
                    description="Test Item",
                    quantity=1,
                    unit_price=100.0,
                    total=100.0
                )
            ],
            currency="USD"
        )
        return ModelResponse(parts=[
            TextPart(content=invoice.model_dump_json())
        ])


async def test_extraction_with_functionmodel(extractor_deps, message_capture):
    """Test para verificar que el agente funciona correctamente con FunctionModel."""
    # Texto de factura de ejemplo
    invoice_text = """
    FACTURA
    Número: TEST-123
    Fecha: 04/03/2025
    Vendedor: Test Company
    """
    
    # Usar FunctionModel para controlar exactamente el comportamiento
    with extraction_agent.override(model=FunctionModel(call_extraction_agent)):
        # Ejecutar el agente
        result = await extraction_agent.run(invoice_text, deps=extractor_deps)
    
    # Verificar que el resultado contiene los datos esperados
    assert result.data.invoice_number == "FUNC-001"
    assert result.data.vendor_name == "FunctionModel Test"
    assert result.data.vendor_tax_id == "123-456-789"
    assert len(result.data.items) == 1
    assert result.data.items[0].description == "Test Item"
    
    # Verificar que se capturaron mensajes
    assert len(message_capture) > 0
