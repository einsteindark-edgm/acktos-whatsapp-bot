import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz del proyecto al PATH de Python
root_dir = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, root_dir)

# Configurar variables de entorno necesarias
os.environ['OPENAI_API_KEY'] = 'dummy_key'

# Importar después de configurar variables de entorno
from pydantic_ai import models
from pydantic_ai.models.test import TestModel

# Desactivar llamadas reales a modelos
models.ALLOW_MODEL_REQUESTS = False

# Importar agentes y dependencias
from agents.data_extraction_agent import extraction_agent
from models.dependencies import ExtractorAgentDependencies
from models.invoice import Invoice, InvoiceItem

# Crear una respuesta simulada para TestModel
class MyTestModel(TestModel):
    def __init__(self):
        super().__init__()
        # Definir una respuesta simulada para el modelo
        self.responses = [
            Invoice(
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
        ]

async def test_extraction_agent():
    print("\nPrueba del agente de extracción de datos...")
    
    # Configurar dependencias
    deps = ExtractorAgentDependencies(model_name="gpt-4", temperature=0.0)
    
    # Reemplazar el modelo con nuestro modelo de prueba
    test_model = MyTestModel()
    
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
        # Ejecutar el agente con el modelo de prueba
        with extraction_agent.override(model=test_model):
            result = await extraction_agent.run(invoice_text, deps=deps)
        
        # Verificar el resultado
        if isinstance(result.data, Invoice):
            print(f"✅ Resultado correcto: {result.data}")
            return True
        else:
            print(f"❌ Resultado incorrecto: {result.data}")
            return False
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

async def main():
    print("🧪 Ejecutando pruebas simplificadas...")
    
    # Ejecutar la prueba
    success = await test_extraction_agent()
    
    if success:
        print("\n✅ Todas las pruebas pasaron correctamente!")
        return 0
    else:
        print("\n❌ Algunas pruebas fallaron!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Error al ejecutar las pruebas: {e}")
        sys.exit(1)
