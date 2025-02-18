from abc import ABC, abstractmethod
from typing import Dict, Any

class VisionProvider(ABC):
    """Interfaz base para proveedores de servicios de visión por computadora"""
    
    @abstractmethod
    async def process_image(
        self,
        image_data: bytes,
        model_name: str,
        api_key: str,
        **kwargs: Dict[str, Any]
    ) -> dict:
        """
        Procesa una imagen y extrae texto e información relevante.
        
        Args:
            image_data: Datos binarios de la imagen
            model_name: Nombre del modelo a utilizar
            api_key: Clave API del proveedor
            kwargs: Argumentos adicionales específicos del proveedor
            
        Returns:
            dict: Diccionario con el texto extraído y metadatos adicionales
        """
        pass
    
    @abstractmethod
    async def validate_api_key(self, api_key: str) -> bool:
        """
        Valida que la clave API sea válida para este proveedor.
        
        Args:
            api_key: Clave API a validar
            
        Returns:
            bool: True si la clave es válida, False en caso contrario
        """
        pass
