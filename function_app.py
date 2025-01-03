import azure.functions as func
import logging
import os

app = func.FunctionApp()

@app.function_name(name="webhook")
@app.route(route="webhook", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def webhook(req: func.HttpRequest) -> func.HttpResponse:
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