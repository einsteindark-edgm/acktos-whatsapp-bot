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

# Importar TestModel
from pydantic_ai.models.test import TestModel

# Importar agentes y dependencias
from agents.data_extraction_agent import extraction_agent
from models.dependencies import ExtractorAgentDependencies
from models.invoice import Invoice, InvoiceItem

# Respuesta simulada para el agente de extracción
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

# Texto de factura de ejemplo
invoice_text = """
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

async def test_extraction_agent():
    print("\nPrueba del agente de extracción de datos...")
    
    try:
        # Configurar dependencias
        deps = ExtractorAgentDependencies(
            model_name="gpt-4",
            temperature=0.0
        )
        
        # Crear modelo de prueba
        test_model = TestModel(custom_result_args=mock_extraction_response)
        
        # Ejecutar el agente con el modelo de prueba
        with extraction_agent.override(model=test_model):
            result = await extraction_agent.run(invoice_text, deps=deps)
        
        # Verificar resultado
        if result and hasattr(result, 'data') and isinstance(result.data, Invoice):
            print(f"✅ Resultado correcto: {result.data.invoice_number}")
            print(f"✅ Vendor: {result.data.vendor_name}")
            print(f"✅ Total: {result.data.total_amount}")
            print(f"✅ Items: {len(result.data.items)}")
            return True
        else:
            print(f"❌ Resultado incorrecto: {result}")
            return False
    except Exception as e:
        print(f"❌ Error en la prueba del agente de extracción: {e}")
        return False

async def main():
    print("🧪 Ejecutando prueba del agente de extracción de datos...")
    
    # Ejecutar prueba
    success = await test_extraction_agent()
    
    if success:
        print("\n✅ La prueba del agente de extracción pasó correctamente!")
        return 0
    else:
        print("\n❌ La prueba del agente de extracción falló!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Error al ejecutar la prueba: {e}")
        sys.exit(1)
