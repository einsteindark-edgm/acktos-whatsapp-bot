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
        verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "acktos2024")
        
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
        
        try:
            body = req.get_json()
            logging.info(f'Message body: {json.dumps(body, indent=2)}')
            
            # Extract message data
            if body.get('object') == 'whatsapp_business_account':
                # Process each entry
                for entry in body.get('entry', []):
                    # Process each change in the entry
                    for change in entry.get('changes', []):
                        if change.get('value', {}).get('messages'):
                            # Process each message
                            for message in change['value']['messages']:
                                message_body = message.get('text', {}).get('body', '')
                                from_number = message.get('from', '')
                                logging.info(f'Message from {from_number}: {message_body}')
                                
                                # Here we'll add message processing logic later
            
            return func.HttpResponse("OK")
            
        except ValueError as e:
            logging.error(f"Error parsing request body: {str(e)}")
            return func.HttpResponse(
                "Invalid request body",
                status_code=400
            )
        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
            return func.HttpResponse(
                f"Error processing message: {str(e)}",
                status_code=500
            )
    
    else:
        return func.HttpResponse(
            "Method not allowed",
            status_code=405
        )