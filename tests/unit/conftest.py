import pytest
import os
import json
from datetime import datetime
from pydantic_ai import models, capture_run_messages
from pydantic_ai.models.test import TestModel

# Configurar variables para testing
os.environ['OPENAI_API_KEY'] = 'sk-test-dummy-key'
os.environ['PYDANTICAI_ALLOW_MODEL_REQUESTS'] = 'false'
models.ALLOW_MODEL_REQUESTS = False  # Prevenir llamadas reales al API

# Importar agentes - envolverlos en try/except para manejar errores de importaciu00f3n
try:
    from agents.vision_agent import vision_agent
except ImportError:
    vision_agent = None
    
try:
    from agents.storage_agent import storage_agent
except ImportError:
    storage_agent = None
    
try:
    from agents.data_extraction_agent import extraction_agent
except ImportError:
    extraction_agent = None

# Importar dependencias y modelos
from models.dependencies import ExtractorAgentDependencies, VisionAgentDependencies, StorageAgentDependencies
from models.invoice import Invoice, InvoiceItem
from tests.unit.mocks.providers import MockVisionProvider, MockStorageProvider
# Configurar pytest para ejecutar pruebas asu00edncronas solo con asyncio
pytest.ini = {
    'asyncio_mode': 'strict',
    'testpaths': ['tests/unit'],
}

# Forzar que pytest-anyio use solo asyncio como backend por defecto
os.environ['PYTEST_ANYIO_BACKEND'] = 'asyncio'

@pytest.fixture
def simple_test_model():
    """Fixture que proporciona un TestModel sencillo para todas las pruebas."""
    return TestModel()
    
@pytest.fixture
def agent_override(request):
    """Fixture genérico para reemplazar el modelo de cualquier agente con TestModel."""
    agent = request.param  # Se usa con @pytest.mark.parametrize
    if agent:
        with agent.override(model=TestModel()):
            yield
    else:
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
        ],
        currency="USD"
    )

@pytest.fixture
def mock_vision_provider():
    """Fixture que proporciona un proveedor de visión simulado."""
    return MockVisionProvider()

@pytest.fixture
def mock_storage_provider():
    """Fixture que proporciona un proveedor de almacenamiento simulado."""
    return MockStorageProvider()

@pytest.fixture
def vision_deps(mock_vision_provider):
    """Fixture que proporciona dependencias para el agente de visión."""
    return VisionAgentDependencies(
        vision_provider=mock_vision_provider,
        model_name="test-model",
        api_key="test-key"
    )

@pytest.fixture
def storage_deps(mock_storage_provider):
    """Fixture que proporciona dependencias para el agente de almacenamiento."""
    return StorageAgentDependencies(storage_provider=mock_storage_provider)

@pytest.fixture
def extractor_deps():
    """Fixture que proporciona dependencias para el agente de extracción."""
    return ExtractorAgentDependencies()

@pytest.fixture
def message_capture():
    """Fixture que captura mensajes durante la ejecución de un agente."""
    with capture_run_messages() as messages:
        yield messages
        
# Desactivar completamente las pruebas de trio
os.environ['PYTEST_ANYIO_BACKEND'] = 'asyncio'  # Forzar solo el uso de asyncio

try:
    import trio
except ImportError:
    # Si trio no está instalado, redefinir pytest.mark.anyio para usar solo asyncio
    _original_anyio = getattr(pytest.mark, 'anyio', None)
    
    def _anyio_asyncio_only(*args, **kwargs):
        # Sobrescribir cualquier backend solicitado con 'asyncio'
        kwargs['backend'] = 'asyncio'
        return _original_anyio(*args, **kwargs) if _original_anyio else pytest.mark.skip(reason='trio no está instalado')
    
    # Reemplazar el marcador anyio original
    if _original_anyio:
        pytest.mark.anyio = _anyio_asyncio_only
        
    # Auto-skip para cualquier prueba que intente usar trio
    @pytest.fixture(autouse=True)
    def skip_trio_tests(request):
        if hasattr(request, 'node') and 'trio' in getattr(request.node, 'name', ''):
            pytest.skip('trio no está instalado')

