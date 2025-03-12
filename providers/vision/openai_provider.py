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
        
        # Imprimir información detallada para depuración
        print(f"OpenAIVisionProvider: Procesando con modelo: {model_name}")
        print(f"OpenAIVisionProvider: API key configurada: {bool(api_key)}")
        
        # Generar un ID de petición para seguimiento
        import uuid
        request_id = str(uuid.uuid4())[:8]
        print(f"OpenAIVisionProvider [{request_id}]: Iniciando petición con modelo {model_name}")
        print(f"OpenAIVisionProvider [{request_id}]: Tamaño de imagen: {len(base64_image)//1024}KB")
        print(f"OpenAIVisionProvider [{request_id}]: Tokens estimados para imagen: ~{len(base64_image)//100} tokens")
        
        # Guardar info de tiempo para detectar timeouts o loops
        import time
        start_time = time.time()
        
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 1000
        }
        
        # Configurar timeout para evitar peticiones que se queden colgadas
        timeout = aiohttp.ClientTimeout(total=30)  # 30 segundos máximo
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.post(
                        f"{self.api_base}/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        # Medir tiempo de respuesta
                        response_time = time.time() - start_time
                        print(f"OpenAIVisionProvider [{request_id}]: Respuesta recibida en {response_time:.2f} segundos")
                        
                        # Procesar respuesta o error
                        if response.status != 200:
                            error_text = await response.text()
                            print(f"OpenAIVisionProvider [{request_id}]: ERROR - Status {response.status}, Respuesta: {error_text}")
                            raise Exception(f"Error en la API de OpenAI: {error_text}")
                        
                        result = await response.json()
                        
                        # Logs de uso para monitorear tokens y costos
                        if "usage" in result:
                            tokens_in = result["usage"].get("prompt_tokens", 0)
                            tokens_out = result["usage"].get("completion_tokens", 0)
                            total_tokens = result["usage"].get("total_tokens", 0)
                            print(f"OpenAIVisionProvider [{request_id}]: Uso de tokens - Entrada: {tokens_in}, Salida: {tokens_out}, Total: {total_tokens}")
                        
                        # Extracto de la respuesta para verificar que es válida
                        text_response = result["choices"][0]["message"]["content"]
                        print(f"OpenAIVisionProvider [{request_id}]: Respuesta exitosa, longitud: {len(text_response)} caracteres")
                        print(f"OpenAIVisionProvider [{request_id}]: Primeros 100 caracteres: {text_response[:100]}...")
                        
                        return {
                            "extracted_text": text_response,
                            "model": model_name,
                            "provider": "openai",
                            "usage": result.get("usage", {})
                        }
                        
                except aiohttp.ClientError as e:
                    error_msg = f"Error de conexión con OpenAI: {str(e)}"
                    print(f"OpenAIVisionProvider [{request_id}]: ERROR - {error_msg}")
                    raise Exception(error_msg)
                    
        except Exception as e:
            # Capturar cualquier excepción para evitar loops infinitos
            print(f"OpenAIVisionProvider [{request_id}]: ERROR FATAL - {str(e)}")
            # Devolver un resultado de error para evitar que el sistema se cuelgue
            return {
                "extracted_text": f"Error procesando la imagen: {str(e)}",
                "model": model_name,
                "provider": "openai",
                "usage": {},
                "error": True
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
