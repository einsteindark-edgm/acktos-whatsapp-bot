import azure.functions as func
import logging
import json
import os
#from utils import send_whatsapp_message

app = func.FunctionApp()

@app.function_name(name="webhook")
@app.route(route="api/webhook", methods=["GET", "POST"], auth_level=func.AuthLevel.ANONYMOUS)
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
                                    #send_whatsapp_message(from_number, response_message)
                                else:
                                    logging.info(f'- Full message content: {json.dumps(message, indent=2)}')
                                    
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
