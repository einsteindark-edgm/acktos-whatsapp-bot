import pytest
from datetime import datetime
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

from agents.storage_agent import storage_agent, StorageResult
from models.dependencies import StorageAgentDependencies
from models.invoice import Invoice, InvoiceItem
from providers.storage.base import StorageProvider

pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False  # Prevenir llamadas reales al API


from tests.unit.mocks.providers import MockStorageProvider


@pytest.fixture
def sample_invoice():
    """Fixture que proporciona una factura de ejemplo para pruebas."""
    return Invoice(
        invoice_number="TEST-001",
        date=datetime.now(),
        vendor_name="Test Vendor",
        vendor_tax_id="123456789",
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


async def test_store_invoice_success():
    """Test para verificar que el agente puede almacenar facturas correctamente."""
    # Crear dependencias con proveedor simulado
    mock_provider = MockStorageProvider()
    deps = StorageAgentDependencies(storage_provider=mock_provider)
    
    # Obtener factura de ejemplo
    invoice = sample_invoice()
    
    # Capturar mensajes durante la ejecuciu00f3n
    with capture_run_messages() as messages:
        # Usar TestModel para simular respuestas del modelo
        with storage_agent.override(model=TestModel()):
            # Ejecutar la herramienta directamente
            result = await storage_agent.tools.store_invoice(
                invoice=invoice,
                deps=deps
            )
    
    # Verificar que el resultado es una instancia de StorageResult
    assert isinstance(result, StorageResult)
    assert result.success is True
    assert result.invoice_id == "INV-001"
    
    # Verificar que la factura se guardu00f3 en el proveedor
    stored_invoice = await mock_provider.get_invoice("INV-001")
    assert stored_invoice is not None
    assert stored_invoice.vendor_name == "Test Vendor"


async def test_verify_storage():
    """Test para verificar que el agente puede verificar el almacenamiento correctamente."""
    # Crear dependencias con proveedor simulado
    mock_provider = MockStorageProvider()
    deps = StorageAgentDependencies(storage_provider=mock_provider)
    
    # Guardar una factura primero
    invoice = sample_invoice()
    invoice_id = await mock_provider.save_invoice(invoice)
    
    # Capturar mensajes durante la ejecuciu00f3n
    with capture_run_messages() as messages:
        # Usar TestModel para simular respuestas del modelo
        with storage_agent.override(model=TestModel()):
            # Verificar una factura existente
            result = await storage_agent.tools.verify_storage(
                invoice_id=invoice_id,
                deps=deps
            )
    
    # Verificar que el resultado es True
    assert result is True
    
    # Verificar una factura inexistente
    with capture_run_messages() as messages:
        with storage_agent.override(model=TestModel()):
            result = await storage_agent.tools.verify_storage(
                invoice_id="NON-EXISTENT",
                deps=deps
            )
    
    # Verificar que el resultado es False
    assert result is False


def call_storage_agent(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """Funciu00f3n personalizada para FunctionModel que simula respuestas especu00edficas."""
    # Primera llamada: llamar a la herramienta store_invoice
    if len(messages) == 1:
        # Crear una factura de ejemplo para el test
        invoice = Invoice(
            invoice_number="FUNC-001",
            date=datetime.now(),
            vendor_name="Function Test",
            vendor_tax_id="987654321",
            total_amount=230.0,
            tax_amount=30.0,
            items=[
                InvoiceItem(
                    description="Function Item",
                    quantity=2,
                    unit_price=100.0,
                    total=200.0
                )
            ],
            currency="EUR"
        )
        
        return ModelResponse(parts=[
            ToolCallPart(
                tool_name='store_invoice',
                args={'invoice': invoice.model_dump()}
            )
        ])
    # Segunda llamada: devolver un resultado personalizado
    else:
        return ModelResponse(parts=[
            TextPart(content='{"invoice_id": "CUSTOM-ID", "success": true, "message": "Almacenado con u00e9xito por FunctionModel"}')
        ])


async def test_run_with_functionmodel():
    """Test para verificar que el agente funciona correctamente con FunctionModel."""
    # Crear dependencias con proveedor simulado
    mock_provider = MockStorageProvider()
    deps = StorageAgentDependencies(storage_provider=mock_provider)
    
    # Capturar mensajes durante la ejecuciu00f3n
    with capture_run_messages() as messages:
        # Usar FunctionModel para controlar exactamente el comportamiento
        with storage_agent.override(model=FunctionModel(call_storage_agent)):
            # Ejecutar el agente
            result = await storage_agent.run("Almacena esta factura", deps=deps)
    
    # Verificar que el resultado contiene los datos personalizados
    assert result.data.invoice_id == "CUSTOM-ID"
    assert result.data.success is True
    assert "FunctionModel" in result.data.message
