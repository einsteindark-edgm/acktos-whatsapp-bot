import azure.functions as func
import logging
import json
import os
from message_handler import WhatsAppMessageHandler

app = func.FunctionApp()

# Get the connection string from environment variable
connection_string = os.environ.get("COSMOSDB_CONNECTION_STRING")
message_handler = WhatsAppMessageHandler(connection_string)

# Main HTTP trigger function for handling WhatsApp webhook requests
@app.route(route="webhook", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "POST"])
def webhook(req: func.HttpRequest) -> func.HttpResponse:
    logging.warning('WhatsApp webhook triggered')
    logging.warning(f'Method: {req.method}')
    logging.warning(f'URL: {req.url}')
    logging.warning(f'Params: {req.params}')

    try:
        if req.method == "GET":
            # Handle webhook verification
            mode = req.params.get("hub.mode")
            token = req.params.get("hub.verify_token")
            challenge = req.params.get("hub.challenge")

            logging.warning(f'Verification request - Mode: {mode}, Token: {token}, Challenge: {challenge}')

            if mode == "subscribe" and token == os.environ["WHATSAPP_VERIFY_TOKEN"]:
                if not challenge:
                    return func.HttpResponse(
                        "No challenge value provided",
                        status_code=400
                    )
                return func.HttpResponse(challenge)
            else:
                return func.HttpResponse(
                    "Invalid verification token",
                    status_code=403
                )

        elif req.method == "POST":
            # Handle incoming messages
            try:
                body = req.get_json()
                logging.warning(f'Received webhook data: {body}')
                
                # Process the message using the handler
                message_handler.process_message(body)
                
                return func.HttpResponse("OK")
            except ValueError as e:
                logging.error(f"Error parsing request body: {str(e)}")
                return func.HttpResponse("Invalid request body", status_code=400)
            except Exception as e:
                logging.error(f"Error processing message: {str(e)}")
                return func.HttpResponse(f"Error processing message: {str(e)}", status_code=500)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)
# Agregar un comentario para forzar un nuevo despliegue
