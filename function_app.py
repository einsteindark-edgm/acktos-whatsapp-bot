import azure.functions as func
import logging
import os
import json
import requests

app = func.FunctionApp()

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

@app.function_name(name="webhook")
@app.route(route="webhook", methods=["GET", "POST"], auth_level=func.AuthLevel.ANONYMOUS)
def webhook(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "GET":
        logging.info('WhatsApp webhook verification request received')
        
        # Get query parameters for webhook verification
        mode = req.params.get("hub.mode")
        token = req.params.get("hub.verify_token")
        challenge = req.params.get("hub.challenge")
        
        # Log verification attempt
        logging.info(f'Verification attempt - Mode: {mode}, Token: {token}, Challenge: {challenge}')
        
        # Verify token from environment variable
        verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN_WEBHOOK")
        
        if mode == "subscribe" and token == verify_token:
            if not challenge:
                return func.HttpResponse(
                    "No challenge value provided",
                    status_code=400
                )
            logging.info(f'Webhook verified successfully')
            return func.HttpResponse(challenge)
        else:
            logging.warning(f'Webhook verification failed')
            return func.HttpResponse(
                "Invalid verification token",
                status_code=403
            )
    
    elif req.method == "POST":
        logging.info('WhatsApp message received')
        logging.info(f'Headers: {dict(req.headers)}')
        
        try:
            # Get the raw body for logging
            raw_body = req.get_body().decode()
            logging.info(f'Raw body: {raw_body}')
            
            # Parse the JSON body
            body = req.get_json()
            logging.info(f'Parsed body: {json.dumps(body, indent=2)}')
            
            # Extract message data
            if body.get('object') == 'whatsapp_business_account':
                logging.info('Message is from WhatsApp Business Account')
                
                # Process each entry
                for entry in body.get('entry', []):
                    logging.info(f'Processing entry: {json.dumps(entry, indent=2)}')
                    
                    # Process each change in the entry
                    for change in entry.get('changes', []):
                        logging.info(f'Processing change: {json.dumps(change, indent=2)}')
                        
                        if change.get('value', {}).get('messages'):
                            # Process each message
                            for message in change['value']['messages']:
                                message_type = message.get('type', 'unknown')
                                from_number = message.get('from', '')
                                timestamp = message.get('timestamp', '')
                                
                                logging.info(f'Message details:')
                                logging.info(f'- From: {from_number}')
                                logging.info(f'- Type: {message_type}')
                                logging.info(f'- Timestamp: {timestamp}')
                                
                                if message_type == 'text':
                                    message_body = message.get('text', {}).get('body', '')
                                    logging.info(f'- Body: {message_body}')
                                    
                                    # Send a response back to the sender
                                    response_message = "Recibí tu mensaje. Contenido:\n" + message_body
                                    send_whatsapp_message(from_number, response_message)
                                else:
                                    logging.info(f'- Full message content: {json.dumps(message, indent=2)}')
            else:
                logging.warning(f'Unexpected object type: {body.get("object")}')
            
            return func.HttpResponse("OK")
            
        except ValueError as e:
            logging.error(f"Error parsing request body: {str(e)}")
            return func.HttpResponse(
                "Invalid request body",
                status_code=400
            )
        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
            logging.exception("Full error details:")
            return func.HttpResponse(
                f"Error processing message: {str(e)}",
                status_code=500
            )
    
    else:
        return func.HttpResponse(
            "Method not allowed",
            status_code=405
        )