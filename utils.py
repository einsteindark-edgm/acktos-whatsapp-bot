import logging
import os
import requests

def send_whatsapp_message(to_number: str, message: str) -> bool:
    """Send a WhatsApp message using the Cloud API
    
    Args:
        to_number (str): The recipient's WhatsApp number
        message (str): The message to send
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        token = os.environ.get("WHATSAPP_TOKEN")
        phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
        
        logging.info(f"Using phone_number_id: {phone_number_id}")
        logging.info(f"Token starts with: {token[:10]}..." if token else "No token found")
        
        if not token or not phone_number_id:
            logging.error("WhatsApp credentials not configured")
            return False
        
        url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
        logging.info(f"Making request to URL: {url}")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logging.info(f"Message sent successfully: {response.json()}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending message: {str(e)}")
        return False
