import os
import aiohttp
import logging
from typing import Dict, Any, Optional

async def send_whatsapp_message(to_number: str, message: str) -> Dict[str, Any]:
    """Envía un mensaje de WhatsApp a través de la API de Meta."""
    try:
        # Validar variables de entorno
        required_env_vars = {
            'WHATSAPP_TOKEN': os.getenv('WHATSAPP_TOKEN'),
            'WHATSAPP_PHONE_NUMBER_ID': os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        }
        missing_vars = [k for k, v in required_env_vars.items() if not v]
        if missing_vars:
            raise ValueError(f"Faltan variables de entorno: {', '.join(missing_vars)}")
        
        # Validar parámetros de entrada
        if not to_number.startswith('+') or len(to_number) < 10:
            raise ValueError("Número de teléfono inválido. Debe estar en formato E.164")
        
        if not message.strip():
            raise ValueError("El mensaje no puede estar vacío")
        
        # Construir solicitud
        url = f"https://graph.facebook.com/v18.0/{required_env_vars['WHATSAPP_PHONE_NUMBER_ID']}/messages"
        headers = {
            "Authorization": f"Bearer {required_env_vars['WHATSAPP_TOKEN']}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message}
        }
        
        # Log de la solicitud
        logging.info(f"Enviando mensaje a WhatsApp:")
        logging.info(f"URL: {url}")
        logging.info(f"Headers: {headers}")
        logging.info(f"Payload: {payload}")

        # Enviar mensaje
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                # Log de la respuesta
                logging.info(f"Respuesta de WhatsApp: {response.status}")
                response_text = await response.text()
                logging.info(f"Contenido de respuesta: {response_text}")
                response.raise_for_status()
                
                return await response.json()
        
    except aiohttp.ClientError as e:
        logging.error(f"Error de API: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Error crítico: {str(e)}")
        raise

async def get_image_from_whatsapp(message: Dict[str, Any]) -> bytes:
    """Obtiene los datos binarios de una imagen de un mensaje de WhatsApp.
    
    Args:
        message: Mensaje de WhatsApp que contiene la imagen
        
    Returns:
        bytes: Datos binarios de la imagen
        
    Raises:
        ValueError: Si no se encuentra la imagen en el mensaje
        Exception: Si hay un error al descargar la imagen
    """
    try:
        # Validar que el mensaje tenga una imagen
        if 'image' not in message:
            raise ValueError("El mensaje no contiene una imagen")
            
        image_id = message['image'].get('id')
        if not image_id:
            raise ValueError("No se encontró el ID de la imagen")
            
        # Obtener variables de entorno
        token = os.getenv('WHATSAPP_TOKEN')
        if not token:
            raise ValueError("No se encontró el token de WhatsApp")
            
        # Construir la URL para descargar la imagen
        url = f"https://graph.facebook.com/v18.0/{image_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Obtener la URL de la imagen
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                image_data = await response.json()
                
                if 'url' not in image_data:
                    raise ValueError("No se encontró la URL de la imagen")
                    
                # Descargar la imagen
                async with session.get(image_data['url'], headers=headers) as img_response:
                    img_response.raise_for_status()
                    return await img_response.read()
                    
    except aiohttp.ClientError as e:
        logging.error(f"Error al descargar la imagen: {str(e)}")
        raise Exception(f"Error al descargar la imagen: {str(e)}")
        
    except Exception as e:
        logging.error(f"Error al procesar la imagen: {str(e)}")
        raise
