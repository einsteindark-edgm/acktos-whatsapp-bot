from dataclasses import dataclass
from providers.vision.base import VisionProvider
from providers.storage.base import StorageProvider

@dataclass
class VisionAgentDependencies:
    """Dependencias para el agente de visión"""
    vision_provider: VisionProvider
    model_name: str
    api_key: str
    image_data: bytes = None  # Campo para almacenar la imagen a procesar

@dataclass
class StorageAgentDependencies:
    """Dependencias para el agente de almacenamiento"""
    storage_provider: StorageProvider

@dataclass
class ExtractorAgentDependencies:
    """Dependencias para el agente extractor de datos"""
    model_name: str = "gpt-4"
    temperature: float = 0.0
    max_tokens: int = 1000
