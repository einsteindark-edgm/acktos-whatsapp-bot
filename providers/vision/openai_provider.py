import base64
from typing import Dict, Any
import aiohttp
from .base import VisionProvider

class OpenAIVisionProvider(VisionProvider):
    """Implementación del proveedor de visión usando OpenAI"""
    
    def __init__(self):
        self.api_base = "https://api.openai.com/v1"
        
    async def process_image(
        self,
        image_data: bytes,
        model_name: str,
        api_key: str,
        **kwargs: Dict[str, Any]
    ) -> dict:
        """
        Procesa una imagen usando la API de visión de OpenAI.
        
        Args:
            image_data: Datos binarios de la imagen
            model_name: Nombre del modelo (ej: "gpt-4-vision-preview")
            api_key: Clave API de OpenAI
            kwargs: Argumentos adicionales
            
        Returns:
            dict: Resultado del procesamiento de la imagen
        """
        # Codificar la imagen en base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Preparar el mensaje para la API
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Esta es una imagen de una factura. Por favor, extrae toda la información relevante incluyendo: número de factura, fecha, vendedor, items, montos y cualquier otro dato importante. Devuelve la información en un formato estructurado."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        # Preparar la solicitud a la API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Error en la API de OpenAI: {error_text}")
                
                result = await response.json()
                return {
                    "extracted_text": result["choices"][0]["message"]["content"],
                    "model": model_name,
                    "provider": "openai",
                    "usage": result.get("usage", {})
                }
    
    async def validate_api_key(self, api_key: str) -> bool:
        """
        Valida la clave API de OpenAI.
        
        Args:
            api_key: Clave API a validar
            
        Returns:
            bool: True si la clave es válida
        """
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/models",
                headers=headers
            ) as response:
                return response.status == 200
