from unittest.mock import AsyncMock, MagicMock
import sys

# Configurar variables de entorno para evitar errores
import os
os.environ['OPENAI_API_KEY'] = 'dummy_key_for_testing'
os.environ['PYDANTICAI_ALLOW_MODEL_REQUESTS'] = 'false'

# Clase para mockeaar respuestas de modelos
class TestModel:
    def __init__(self):
        pass
        
    async def chat(self, messages, **kwargs):
        return {'choices': [{'message': {'content': 'test response'}}]}

# Mockear modelos concretos
class VisionResult:
    class Data:
        def __init__(self):
            self.extracted_text = 'Este es un texto extraído de prueba'
            
    def __init__(self):
        self.data = self.Data()
        
class Invoice:
    def __init__(self):
        self.invoice_number = 'INV-001'
        self.total_amount = '100.00'
        self.currency = 'USD'
        self.vendor_name = 'Test Vendor'
        self.date = '2023-01-01'
        
    def model_dump(self):
        return {
            'invoice_number': self.invoice_number,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'vendor_name': self.vendor_name,
            'date': self.date
        }
        
class StorageResult:
    def __init__(self):
        self.invoice_id = 'INV-001'
        self.success = True
        self.message = 'Factura almacenada correctamente'

# Función para aplicar mocks
def apply_mocks():
    # Mockear PydanticAI
    sys.modules['pydantic_ai'] = MagicMock()
    sys.modules['pydantic_ai'].models = MagicMock()
    sys.modules['pydantic_ai'].models.TestModel = TestModel
    sys.modules['pydantic_ai'].models.ALLOW_MODEL_REQUESTS = False
    sys.modules['pydantic_ai'].Agent = MagicMock()

    # Mockear OpenAI
    sys.modules['openai'] = MagicMock()
    sys.modules['openai'].AsyncOpenAI = MagicMock()

    # Mocks para los agentes
    sys.modules['agents'] = MagicMock()
    sys.modules['agents.vision_agent'] = MagicMock()
    sys.modules['agents.extraction_agent'] = MagicMock()
    sys.modules['agents.storage_agent'] = MagicMock()

    # Configurar modelos concretos
    sys.modules['agents.vision_agent'].VisionResult = VisionResult
    sys.modules['models.invoice'] = MagicMock()
    sys.modules['models.invoice'].Invoice = Invoice
    sys.modules['agents.storage_agent'].StorageResult = StorageResult

    # Mockear agentes concretos
    sys.modules['agents.vision_agent'].vision_agent = MagicMock()
    sys.modules['agents.vision_agent'].vision_agent.run = AsyncMock(return_value=VisionResult())

    sys.modules['agents.extraction_agent'] = MagicMock()
    sys.modules['agents.extraction_agent'].extraction_agent = MagicMock()
    sys.modules['agents.extraction_agent'].extraction_agent.run = AsyncMock(return_value=MagicMock(data=Invoice()))

    sys.modules['agents.storage_agent'].storage_agent = MagicMock()
    sys.modules['agents.storage_agent'].storage_agent.run = AsyncMock(return_value=MagicMock(data=StorageResult()))

    print("Mocks aplicados con éxito")
