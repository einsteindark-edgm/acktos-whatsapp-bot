import os
import sys
import asyncio
from datetime import datetime

# Configurar variables de entorno necesarias
os.environ['OPENAI_API_KEY'] = 'dummy_key'

# Importar después de configurar variables de entorno
from pydantic_ai import models
from pydantic_ai.models.test import TestModel
from pydantic_ai import capture_run_messages
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, UserPromptPart

# Desactivar llamadas reales a modelos
models.ALLOW_MODEL_REQUESTS = False

# Importar agentes y dependencias
from agents.data_extraction_agent import extraction_agent
from models.dependencies import ExtractorAgentDependencies
from models.invoice import Invoice, InvoiceItem
from tests.unit.mocks.providers import MockVisionProvider, MockStorageProvider

# Clase personalizada para TestModel que devuelve una respuesta predefinida
class CustomTestModel(TestModel):
    async def predict(self, messages, **kwargs):
        # Crear una factura de ejemplo como respuesta
        invoice = Invoice(
            invoice_number="INV-001",
            date=datetime.now(),
            vendor_name="Tech Solutions Inc",
            vendor_tax_id="123456789",
            total_amount=1150.00,
            tax_amount=150.00,
            items=[
                InvoiceItem(
                    description="Laptop Dell XPS 13",
                    quantity=1,
                    unit_price=1000.00,
                    total=1000.00
                )
            ]
        )
        
        # Devolver una respuesta simulada
        return ModelResponse(
            choices=[
                ModelMessage(
                    content=TextPart(text=str(invoice)),
                    role="assistant"
                )
            ]
        )

async def test_parse_invoice_text():
    """Test para verificar que el agente puede analizar texto de factura correctamente."""
    # Configurar dependencias
    extractor_deps = ExtractorAgentDependencies(model_name="gpt-4", temperature=0.0)
    
    # Reemplazar el modelo con nuestro CustomTestModel
    with extraction_agent.override(model=CustomTestModel()):
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
        
        try:
            # Capturar mensajes
            with capture_run_messages() as messages:
                # Ejecutar el agente
                result = await extraction_agent.run(invoice_text, deps=extractor_deps)
                
                # Verificar que el resultado es una instancia de Invoice
                if not isinstance(result.data, Invoice):
                    print(f"❌ Error: El resultado no es una instancia de Invoice, es {type(result.data)}")
                    return False
                
                # Verificar que los mensajes tienen la estructura esperada
                if len(messages) == 0:
                    print("❌ Error: No se capturaron mensajes")
                    return False
                
                # Verificar datos específicos de la factura
                invoice = result.data
                assert invoice.invoice_number == "INV-001"
                assert invoice.vendor_name == "Tech Solutions Inc"
                assert invoice.vendor_tax_id == "123456789"
                assert invoice.total_amount == 1150.00
                
                print("✅ test_parse_invoice_text: PASSED")
                return True
        except Exception as e:
            print(f"❌ Error en test_parse_invoice_text: {e}")
            return False

async def run_tests():
    """Ejecutar todos los tests"""
    print("\n🧪 Ejecutando tests para el agente de extracción de datos...\n")
    
    tests = [
        test_parse_invoice_text()
    ]
    
    results = await asyncio.gather(*tests)
    
    if all(results):
        print("\n✅ Todos los tests pasaron correctamente!")
        return 0
    else:
        print("\n❌ Algunos tests fallaron!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_tests())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Error al ejecutar los tests: {e}")
        sys.exit(1)
