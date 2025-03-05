import pytest
import os
import sys
from datetime import datetime
from pydantic_ai import models, capture_run_messages
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel

# Importar los agentes y modelos necesarios
from agents.data_extraction_agent import extraction_agent
from agents.vision_agent import vision_agent
from agents.storage_agent import storage_agent
from models.dependencies import ExtractorAgentDependencies, VisionAgentDependencies, StorageAgentDependencies
from models.invoice import Invoice, InvoiceItem
from tests.unit.mocks.providers import MockVisionProvider, MockStorageProvider

# Desactivar llamadas reales a modelos durante las pruebas
models.ALLOW_MODEL_REQUESTS = False
os.environ['OPENAI_API_KEY'] = 'dummy_key'

@pytest.fixture
def override_extraction_agent():
    """Fixture para reemplazar el modelo del agente de extracción con TestModel."""
    with extraction_agent.override(model=TestModel()):
        yield

@pytest.fixture
def override_vision_agent():
    """Fixture para reemplazar el modelo del agente de visión con TestModel."""
    with vision_agent.override(model=TestModel()):
        yield

@pytest.fixture
def override_storage_agent():
    """Fixture para reemplazar el modelo del agente de almacenamiento con TestModel."""
    with storage_agent.override(model=TestModel()):
        yield

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
        ]
    )

@pytest.fixture
def mock_vision_provider():
    """Fixture que proporciona un proveedor de visión simulado."""
    return MockVisionProvider(api_key="dummy_key")

@pytest.fixture
def mock_storage_provider():
    """Fixture que proporciona un proveedor de almacenamiento simulado."""
    return MockStorageProvider()

@pytest.fixture
def vision_deps(mock_vision_provider):
    """Fixture que proporciona dependencias para el agente de visión."""
    return VisionAgentDependencies(
        vision_provider=mock_vision_provider,
        model_name="gpt-4-vision",
        api_key="dummy_key"
    )

@pytest.fixture
def storage_deps(mock_storage_provider):
    """Fixture que proporciona dependencias para el agente de almacenamiento."""
    return StorageAgentDependencies(storage_provider=mock_storage_provider)

@pytest.fixture
def extractor_deps():
    """Fixture que proporciona dependencias para el agente de extracción."""
    return ExtractorAgentDependencies(model_name="gpt-4", temperature=0.0)

@pytest.fixture
def message_capture():
    """Fixture que captura mensajes durante la ejecución de un agente."""
    with capture_run_messages() as messages:
        yield messages
