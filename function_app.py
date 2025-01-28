import azure.functions as func
import logging
import os
import json
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

def process_incoming_message(body):
    if body.get("object"):
        if (
            "entry" in body
            and body["entry"]
            and "changes" in body["entry"][0]
            and body["entry"][0]["changes"]
            and "value" in body["entry"][0]["changes"][0]
        ):
            value = body["entry"][0]["changes"][0]["value"]
            
            if (
                "messages" in value
                and value["messages"]
                and len(value["messages"]) > 0
            ):
                for message in value["messages"]:
                    from_number = message.get("from")
                    message_type = message.get("type")
                    
                    logging.info("Message details:")
                    logging.info(f"- From: {from_number}")
                    logging.info(f"- Type: {message_type}")
                    logging.info(f"- Timestamp: {message.get('timestamp')}")
                    
                    if message_type == 'text':
                        message_body = message.get('text', {}).get('body', '')
                        logging.info(f'- Body: {message_body}')
                        
                        # Send a response back to the sender
                        response_message = "Recibí tu mensaje. Contenido:\n" + message_body
                        send_whatsapp_message(from_number, response_message)
                    else:
                        logging.info(f'- Full message content: {json.dumps(message, indent=2)}')

# Azure Function app code
app = func.FunctionApp()

@app.function_name(name="webhook")
@app.route(route="webhook", auth_level=func.AuthLevel.ANONYMOUS)
def webhook(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        if req.method == "GET":
            # Handle webhook verification
            mode = req.params.get("hub.mode")
            token = req.params.get("hub.verify_token")
            challenge = req.params.get("hub.challenge")
            
            verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN_WEBHOOK")
            
            if mode == "subscribe" and token == verify_token:
                if not challenge:
                    return func.HttpResponse(
                        "Missing challenge parameter.",
                        status_code=400
                    )
                    
                return func.HttpResponse(
                    challenge,
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    "Failed validation. Make sure the validation tokens match.",
                    status_code=403
                )
                
        elif req.method == "POST":
            # Handle incoming messages
            try:
                body = req.get_json()
                logging.info(f"Received webhook data: {json.dumps(body, indent=2)}")
                process_incoming_message(body)
            except ValueError as e:
                logging.error(f"Error parsing JSON: {str(e)}")
                return func.HttpResponse(
                    "Invalid JSON payload",
                    status_code=400
                )
                
            return func.HttpResponse(
                "Event received",
                status_code=200
            )
            
        return func.HttpResponse(
            "Method not supported",
            status_code=405
        )
            
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )