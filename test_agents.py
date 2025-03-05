import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configurar variables de entorno necesarias
os.environ['OPENAI_API_KEY'] = 'dummy_key'

# Desactivar llamadas reales a modelos
from pydantic_ai import models
models.ALLOW_MODEL_REQUESTS = False

# Importar agentes y dependencias
from agents.data_extraction_agent import extraction_agent
from agents.vision_agent import vision_agent
from agents.storage_agent import storage_agent
from models.dependencies import ExtractorAgentDependencies, VisionAgentDependencies, StorageAgentDependencies
from models.invoice import Invoice, InvoiceItem
from tests.unit.mocks.providers import MockVisionProvider, MockStorageProvider

# Crear un modelo de prueba personalizado para cada agente
class MockModel:
    def __init__(self, response):
        self.response = response
    
    async def __call__(self, *args, **kwargs):
        return self.response

# Respuestas simuladas para cada agente
mock_vision_response = {
    "extracted_text": "FACTURA\nNúmero: INV-001\nFecha: 17/02/2024\nVendedor: Test Company\nNIT: 123456789\n\nItem 1 - 100.00 x 1 = 100.00\n\nSubtotal: 100.00\nIVA: 19.00\nTotal: 119.00 USD"
}

mock_extraction_response = Invoice(
    invoice_number="INV-001",
    date=datetime.now(),
    vendor_name="Test Company",
    vendor_tax_id="123456789",
    total_amount=119.00,
    tax_amount=19.00,
    items=[
        InvoiceItem(
            description="Item 1",
            quantity=1,
            unit_price=100.00,
            total=100.00
        )
    ]
)

mock_storage_response = "INV-001"

async def test_vision_agent():
    print("\nPrueba del agente de visión...")
    
    try:
        # Configurar dependencias
        vision_provider = MockVisionProvider()
        deps = VisionAgentDependencies(
            vision_provider=vision_provider,
            model_name="gpt-4-vision",
            api_key="valid-key"
        )
        
        # Crear modelo mock
        mock_model = MockModel(mock_vision_response)
        
        # Ejecutar el agente con el modelo mock
        with vision_agent.override(model=mock_model):
            result = await vision_agent.run(b"dummy_image_data", deps=deps)
        
        # Verificar resultado
        if result and "extracted_text" in result:
            print(f"✅ Resultado correcto: {result['extracted_text'][:30]}...")
            return True
        else:
            print(f"❌ Resultado incorrecto: {result}")
            return False
    except Exception as e:
        print(f"❌ Error en la prueba del agente de visión: {e}")
        return False

async def test_extraction_agent():
    print("\nPrueba del agente de extracción de datos...")
    
    try:
        # Configurar dependencias
        deps = ExtractorAgentDependencies(
            model_name="gpt-4",
            temperature=0.0
        )
        
        # Crear modelo mock
        mock_model = MockModel(mock_extraction_response)
        
        # Texto de factura de ejemplo
        invoice_text = mock_vision_response["extracted_text"]
        
        # Ejecutar el agente con el modelo mock
        with extraction_agent.override(model=mock_model):
            result = await extraction_agent.run(invoice_text, deps=deps)
        
        # Verificar resultado
        if result and hasattr(result, 'data') and isinstance(result.data, Invoice):
            print(f"✅ Resultado correcto: {result.data.invoice_number}")
            return True
        else:
            print(f"❌ Resultado incorrecto: {result}")
            return False
    except Exception as e:
        print(f"❌ Error en la prueba del agente de extracción: {e}")
        return False

async def test_storage_agent():
    print("\nPrueba del agente de almacenamiento...")
    
    try:
        # Configurar dependencias
        storage_provider = MockStorageProvider()
        deps = StorageAgentDependencies(
            storage_provider=storage_provider
        )
        
        # Crear modelo mock
        mock_model = MockModel(mock_storage_response)
        
        # Crear factura de prueba
        invoice = mock_extraction_response
        
        # Ejecutar el agente con el modelo mock
        with storage_agent.override(model=mock_model):
            result = await storage_agent.run(invoice, deps=deps)
        
        # Verificar resultado
        if result and isinstance(result, str):
            print(f"✅ Resultado correcto: {result}")
            
            # Verificar que la factura se guardó correctamente
            stored_invoice = await storage_provider.get_invoice(result)
            if stored_invoice:
                print(f"✅ Factura guardada correctamente: {stored_invoice.invoice_number}")
                return True
            else:
                print("❌ Factura no encontrada en el almacenamiento")
                return False
        else:
            print(f"❌ Resultado incorrecto: {result}")
            return False
    except Exception as e:
        print(f"❌ Error en la prueba del agente de almacenamiento: {e}")
        return False

async def main():
    print("🧪 Ejecutando pruebas de agentes con mocks...")
    
    # Ejecutar pruebas
    success_vision = await test_vision_agent()
    success_extraction = await test_extraction_agent()
    success_storage = await test_storage_agent()
    
    if success_vision and success_extraction and success_storage:
        print("\n✅ Todas las pruebas de agentes pasaron correctamente!")
        return 0
    else:
        print("\n❌ Algunas pruebas de agentes fallaron!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Error al ejecutar las pruebas: {e}")
        sys.exit(1)
