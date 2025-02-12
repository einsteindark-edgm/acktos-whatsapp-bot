import os
import requests
import logging
from typing import Dict, Any

def send_whatsapp_message(to_number: str, message: str) -> Dict[str, Any]:
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
        
        # Enviar mensaje
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        logging.error(f"Error de API: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logging.error(f"Error crítico: {str(e)}")
        raise
