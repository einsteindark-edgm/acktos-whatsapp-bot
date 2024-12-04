import logging
import azure.functions as func
from ..database import DatabaseManager
from ..message_handler import WhatsAppMessageHandler

db_manager = DatabaseManager()
message_handler = WhatsAppMessageHandler()

async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('WhatsApp webhook triggered')
    
    try:
        # Handle WhatsApp verification challenge
        if req.method == "GET":
            mode = req.params.get('hub.mode')
            token = req.params.get('hub.verify_token')
            challenge = req.params.get('hub.challenge')
            
            if mode and token:
                if mode == 'subscribe' and token == 'your_verify_token':
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

        # Check if driver is registered
        driver = await db_manager.check_driver_registration(parsed_message['phone_number'])
        
        if driver:
            # Process and save service request for registered driver
            service_details = message_handler.extract_service_details(parsed_message['message_text'])
            request_data = {
                **parsed_message,
                **service_details,
                'driver_id': driver['id'] if isinstance(driver, dict) and 'id' in driver else str(driver['_id'])
            }
            await db_manager.save_service_request(request_data)
            return func.HttpResponse("Service request processed successfully", status_code=200)
        else:
            # Log unregistered attempt
            attempt_data = {
                **parsed_message,
                'status': 'unregistered_driver'
            }
            await db_manager.log_unregistered_attempt(attempt_data)
            return func.HttpResponse("Unregistered driver", status_code=403)
        
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        return func.HttpResponse(f"Error processing message: {str(e)}", status_code=500)
