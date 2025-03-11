from fastapi import Depends, HTTPException, status
from typing import Annotated, Generator

from app.config import settings
from providers.vision.openai_provider import OpenAIVisionProvider
from providers.storage.mongodb_provider import MongoDBProvider
from models.dependencies import VisionAgentDependencies, StorageAgentDependencies, ExtractorAgentDependencies

# Vision Provider
def get_vision_provider() -> OpenAIVisionProvider:
    """Proporciona el proveedor de visión"""
    return OpenAIVisionProvider()

# Storage Provider
def get_storage_provider() -> MongoDBProvider:
    """Proporciona el proveedor de almacenamiento"""
    return MongoDBProvider(connection_string=settings.MONGO_CONNECTION_STRING)

# Dependencias para agentes
def get_vision_deps(
    vision_provider: Annotated[OpenAIVisionProvider, Depends(get_vision_provider)]
) -> VisionAgentDependencies:
    """Proporciona las dependencias para el agente de visión"""
    return VisionAgentDependencies(
        vision_provider=vision_provider,
        model_name=settings.VISION_MODEL,
        api_key=settings.OPENAI_API_KEY
    )

def get_storage_deps(
    storage_provider: Annotated[MongoDBProvider, Depends(get_storage_provider)]
) -> StorageAgentDependencies:
    """Proporciona las dependencias para el agente de almacenamiento"""
    return StorageAgentDependencies(
        storage_provider=storage_provider
    )

def get_extractor_deps() -> ExtractorAgentDependencies:
    """Proporciona las dependencias para el agente extractor"""
    return ExtractorAgentDependencies(
        model_name=settings.EXTRACTION_MODEL,
        temperature=0.0,
        max_tokens=1000
    )
