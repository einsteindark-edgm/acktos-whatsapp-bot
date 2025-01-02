import azure.functions as func
import logging
import json
import os
from message_handler import WhatsAppMessageHandler

app = func.FunctionApp()

# Initialize WhatsAppMessageHandler with Cosmos DB connection
connection_string = os.environ["COSMOSDB_CONNECTION_STRING"]
message_handler = WhatsAppMessageHandler(connection_string)

# Main HTTP trigger function for handling WhatsApp webhook requests
# This endpoint handles both GET (for verification) and POST (for messages) requests
# Updated for new deployment test - 2025-01-02
@app.function_name(name="WhatsAppWebhook")
# Webhook endpoint for WhatsApp messages
@app.route(route="webhook", auth_level=func.AuthLevel.FUNCTION)
async def whatsapp_webhook(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('WhatsApp webhook triggered')
    
    try:
        # Handle WhatsApp verification challenge
        if req.method == "GET":
            mode = req.params.get('hub.mode')
            token = req.params.get('hub.verify_token')
            challenge = req.params.get('hub.challenge')
            
            if mode and token:
                if mode == 'subscribe' and token == os.environ.get('WHATSAPP_VERIFY_TOKEN'):
                    return func.HttpResponse(challenge, status_code=200)
                else:
                    return func.HttpResponse('Forbidden', status_code=403)
        
        # Get request body
        try:
            body = req.get_json()
        except ValueError:
            return func.HttpResponse("Invalid JSON", status_code=400)

        # Process incoming message
        parsed_message = message_handler.parse_whatsapp_message(body)
        if not parsed_message:
            return func.HttpResponse("Invalid message format", status_code=400)

        # Log the parsed message for debugging
        logging.info(f"Parsed message: {json.dumps(parsed_message)}")

        # Save message to Cosmos DB
        if message_handler.save_message(parsed_message):
            logging.info(f"Message saved successfully: {parsed_message['id']}")
            return func.HttpResponse("Message processed successfully", status_code=200)
        else:
            return func.HttpResponse("Error saving message", status_code=500)
        
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        return func.HttpResponse(f"Error processing message: {str(e)}", status_code=500)
# Agregar un comentario para forzar un nuevo despliegue
