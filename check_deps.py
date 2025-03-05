import os
import sys

# Configurar variables de entorno necesarias
os.environ['OPENAI_API_KEY'] = 'dummy_key'

# Verificar que podemos importar las bibliotecas necesarias
try:
    print("Importando pydantic_ai...")
    from pydantic_ai import models, capture_run_messages
    from pydantic_ai.models.test import TestModel
    print("✅ pydantic_ai importado correctamente")
    
    print("\nVerificando versión de pydantic_ai...")
    import pydantic_ai
    print(f"✅ Versión de pydantic_ai: {pydantic_ai.__version__}")
    
    print("\nImportando agentes...")
    from agents.data_extraction_agent import extraction_agent
    from agents.vision_agent import vision_agent
    from agents.storage_agent import storage_agent
    print("✅ Agentes importados correctamente")
    
    print("\nImportando modelos...")
    from models.dependencies import ExtractorAgentDependencies, VisionAgentDependencies, StorageAgentDependencies
    from models.invoice import Invoice, InvoiceItem
    print("✅ Modelos importados correctamente")
    
    print("\nImportando mocks...")
    from tests.unit.mocks.providers import MockVisionProvider, MockStorageProvider
    print("✅ Mocks importados correctamente")
    
    print("\n✅ Todas las dependencias se importaron correctamente!")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error al importar dependencias: {e}")
    sys.exit(1)
