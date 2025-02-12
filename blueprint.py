import azure.functions as func
import logging
import json
import os
from utils import send_whatsapp_message

bp = func.Blueprint()

def handle_webhook(req: func.HttpRequest) -> func.HttpResponse:
    """Función principal que maneja las solicitudes del webhook"""
    try:
        if req.method == "GET":
            return handle_verification(req)
        elif req.method == "POST":
            return handle_messages(req)
        else:
            return func.HttpResponse(
                "Method not supported",
                status_code=405
            )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )

def handle_verification(req: func.HttpRequest) -> func.HttpResponse:
    """Maneja la verificación del webhook"""
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

def handle_messages(req: func.HttpRequest) -> func.HttpResponse:
    """Maneja los mensajes entrantes"""
    try:
        body_text = req.get_body().decode('utf-8')
        logging.info(f'Raw request body: {body_text}')
        body = json.loads(body_text)
        logging.info(f"Received webhook data: {json.dumps(body, indent=2)}")
        
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
                        # Asegurarse de que el número esté en formato E.164
                        from_number = message.get("from")
                        if from_number and not from_number.startswith("+"):
                            from_number = "+" + from_number
                        logging.info(f"Número formateado: {from_number}")
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
                            
                    return func.HttpResponse(
                        "Event received",
                        status_code=200
                    )
            
        return func.HttpResponse(
            "Invalid message format",
            status_code=400
        )
                
    except ValueError as e:
        logging.error(f"Error parsing JSON: {str(e)}")
        return func.HttpResponse(
            "Invalid JSON payload",
            status_code=400
        )

@bp.function_name(name="webhook")
@bp.route(route="webhook", methods=["GET", "POST"], auth_level=func.AuthLevel.ANONYMOUS)
def webhook(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'Python HTTP trigger function processed a {req.method} request with URL {req.url}')
    logging.info(f'Headers: {dict(req.headers)}')
    return handle_webhook(req)
