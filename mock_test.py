import os
import sys
import asyncio
from datetime import datetime

# Configurar variables de entorno necesarias
os.environ['OPENAI_API_KEY'] = 'dummy_key'

# Importar modelos y dependencias
from models.invoice import Invoice, InvoiceItem
from models.dependencies import ExtractorAgentDependencies, VisionAgentDependencies, StorageAgentDependencies
from tests.unit.mocks.providers import MockVisionProvider, MockStorageProvider

async def test_mock_providers():
    print("\nPrueba de proveedores mock...")
    
    try:
        # Crear proveedores mock
        vision_provider = MockVisionProvider()
        storage_provider = MockStorageProvider()
        
        # Probar vision_provider
        print("Probando MockVisionProvider...")
        api_key_valid = await vision_provider.validate_api_key("valid-key")
        print(f"API key válida: {api_key_valid}")
        
        # Probar process_image
        image_result = await vision_provider.process_image(
            image_data=b"dummy_image_data",
            model_name="gpt-4-vision",
            api_key="valid-key"
        )
        print(f"Texto extraído: {image_result['extracted_text'][:30]}...")
        
        # Probar storage_provider
        print("\nProbando MockStorageProvider...")
        invoice = Invoice(
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
        
        # Guardar factura
        invoice_id = await storage_provider.save_invoice(invoice)
        print(f"Factura guardada con ID: {invoice_id}")
        
        # Obtener factura
        retrieved_invoice = await storage_provider.get_invoice(invoice_id)
        print(f"Factura recuperada: {retrieved_invoice.invoice_number}")
        
        # Listar facturas
        invoices = await storage_provider.list_invoices()
        print(f"Número de facturas: {len(invoices)}")
        
        # Eliminar factura
        await storage_provider.delete_invoice(invoice_id)
        print("Factura eliminada correctamente")
        
        print("✅ Prueba de proveedores mock completada con éxito")
        return True
    except Exception as e:
        print(f"❌ Error en la prueba de proveedores mock: {e}")
        return False

async def test_dependencies():
    print("\nPrueba de dependencias...")
    
    try:
        # Crear dependencias
        vision_provider = MockVisionProvider()
        storage_provider = MockStorageProvider()
        
        vision_deps = VisionAgentDependencies(
            vision_provider=vision_provider,
            model_name="gpt-4-vision",
            api_key="dummy_key"
        )
        
        storage_deps = StorageAgentDependencies(
            storage_provider=storage_provider
        )
        
        extractor_deps = ExtractorAgentDependencies(
            model_name="gpt-4",
            temperature=0.0
        )
        
        print(f"VisionAgentDependencies: {vision_deps}")
        print(f"StorageAgentDependencies: {storage_deps}")
        print(f"ExtractorAgentDependencies: {extractor_deps}")
        
        print("✅ Prueba de dependencias completada con éxito")
        return True
    except Exception as e:
        print(f"❌ Error en la prueba de dependencias: {e}")
        return False

async def main():
    print("🧪 Ejecutando pruebas de mocks y dependencias...")
    
    # Ejecutar pruebas
    success_mock = await test_mock_providers()
    success_deps = await test_dependencies()
    
    if success_mock and success_deps:
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
