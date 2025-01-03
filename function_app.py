import azure.functions as func
import logging
import os
import json

app = func.FunctionApp()

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