import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configurar variables de entorno necesarias
os.environ['OPENAI_API_KEY'] = 'dummy_key'

# Desactivar llamadas reales a modelos
from pydantic_ai import models
from pydantic_ai import capture_run_messages
models.ALLOW_MODEL_REQUESTS = False

# Importar TestModel
from pydantic_ai.models.test import TestModel

# Importar agentes y dependencias
from agents.vision_agent import vision_agent, VisionResult
from agents.data_extraction_agent import extraction_agent
from models.dependencies import VisionAgentDependencies, ExtractorAgentDependencies
from models.invoice import Invoice, InvoiceItem
from tests.unit.mocks.providers import MockVisionProvider

# Datos de imagen simulados
dummy_image_data = b"dummy_image_data"

# Texto extraído simulado
extracted_text = """
FACTURA
Número: INV-001
Fecha: 17/02/2024
Vendedor: Test Company
NIT: 123456789

Item 1 - 100.00 x 1 = 100.00

Subtotal: 100.00
IVA: 19.00
Total: 119.00 USD
"""

# Respuesta simulada para el proceso_invoice_image
vision_expected_result = VisionResult(
    extracted_text=extracted_text,
    confidence=0.95,
    provider="mock_provider",
    model="gpt-4-vision"
)

# Respuesta simulada para el agente de extracción
extraction_expected_result = Invoice(
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

async def test_vision_extraction_e2e():
    print("\nPrueba end-to-end de visión y extracción...")
    
    try:
        # Configurar dependencias para el agente de visión
        vision_provider = MockVisionProvider()
        vision_deps = VisionAgentDependencies(
            vision_provider=vision_provider,
            model_name="gpt-4-vision",
            api_key="valid-key"
        )
        
        # Configurar dependencias para el agente de extracción
        extraction_deps = ExtractorAgentDependencies(
            model_name="gpt-4",
            temperature=0.0
        )
        
        # Crear respuesta para el MockVisionProvider
        mock_provider_response = {
            "extracted_text": extracted_text,
            "provider": "mock_provider",
            "model": "gpt-4-vision"
        }
        
        # Configurar el mock para que devuelva nuestra respuesta simulada
        async def mock_process_image(*args, **kwargs):
            return mock_provider_response
        
        # Reemplazar el método original con nuestro mock
        vision_provider.process_image = mock_process_image
        
        # PASO 1: Ejecutar el agente de visión con TestModel
        print("\nPASO 1: Procesando imagen con el agente de visión...")
        with capture_run_messages() as vision_messages:
            with vision_agent.override(model=TestModel(custom_result_args=vision_expected_result)):
                vision_result = await vision_agent.run(dummy_image_data, deps=vision_deps)
        
        # Verificar resultado de visión
        if not (vision_result and hasattr(vision_result, 'data') and isinstance(vision_result.data, VisionResult)):
            print(f"[FAIL] Resultado de visión incorrecto: {vision_result}")
            return False
        
        vision_data = vision_result.data
        print(f"[PASS] Texto extraído: {vision_data.extracted_text[:30]}...")
        print(f"[PASS] Proveedor: {vision_data.provider}")
        print(f"[PASS] Modelo: {vision_data.model}")
        
        # PASO 2: Usar el texto extraído para el agente de extracción
        print("\nPASO 2: Extrayendo datos estructurados del texto...")
        with capture_run_messages() as extraction_messages:
            with extraction_agent.override(model=TestModel(custom_result_args=extraction_expected_result)):
                extraction_result = await extraction_agent.run(vision_data.extracted_text, deps=extraction_deps)
        
        # Verificar resultado de extracción
        if not (extraction_result and hasattr(extraction_result, 'data') and isinstance(extraction_result.data, Invoice)):
            print(f"[FAIL] Resultado de extracción incorrecto: {extraction_result}")
            return False
        
        invoice_data = extraction_result.data
        print(f"[PASS] Número de factura: {invoice_data.invoice_number}")
        print(f"[PASS] Vendedor: {invoice_data.vendor_name}")
        print(f"[PASS] Monto total: {invoice_data.total_amount} {invoice_data.currency if hasattr(invoice_data, 'currency') else ''}")
        print(f"[PASS] Cantidad de items: {len(invoice_data.items)}")
        
        # Verificar que los datos extraídos coinciden con lo esperado
        assert invoice_data.invoice_number == extraction_expected_result.invoice_number
        assert invoice_data.vendor_name == extraction_expected_result.vendor_name
        assert invoice_data.total_amount == extraction_expected_result.total_amount
        assert len(invoice_data.items) == len(extraction_expected_result.items)
        
        print("\n[PASS] La prueba end-to-end completó exitosamente!")
        return True
    except Exception as e:
        print(f"[FAIL] Error en la prueba end-to-end: {e}")
        return False

async def main():
    print("Ejecutando prueba end-to-end de visión y extracción...")
    
    # Ejecutar prueba
    success = await test_vision_extraction_e2e()
    
    if success:
        print("\n[PASS] La prueba end-to-end pasó correctamente!")
        return 0
    else:
        print("\n[FAIL] La prueba end-to-end falló!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar la prueba: {e}")
        sys.exit(1)
