import azure.functions as func
import logging
import json
import os
from utils import send_whatsapp_message
from agents.vision_agent import vision_agent
from agents.data_extraction_agent import extraction_agent
from agents.storage_agent import storage_agent
from models.dependencies import VisionAgentDependencies, ExtractorAgentDependencies, StorageAgentDependencies
from providers.vision.openai_provider import OpenAIVisionProvider
from providers.storage.cosmosdb_provider import CosmosDBProvider

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

async def handle_messages(req: func.HttpRequest) -> func.HttpResponse:
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
                        
                        if message_type == 'image':
                            try:
                                # 1. Configurar dependencias
                                vision_deps = VisionAgentDependencies(
                                    vision_provider=OpenAIVisionProvider(),
                                    model_name="gpt-4-vision-preview",
                                    api_key=os.environ["OPENAI_API_KEY"]
                                )
                                
                                storage_deps = StorageAgentDependencies(
                                    storage_provider=CosmosDBProvider(
                                        connection_string=os.environ["COSMOSDB_CONNECTION_STRING"]
                                    )
                                )
                                
                                # 2. Obtener la imagen
                                image_data = await get_image_from_whatsapp(message)
                                
                                # 3. Procesar la imagen con Vision Agent
                                vision_result = await vision_agent.run(
                                    "Extract text from this invoice",
                                    deps=vision_deps,
                                    files={"image": image_data}
                                )
                                
                                # 4. Extraer datos estructurados
                                extraction_result = await extraction_agent.run(
                                    vision_result.data.extracted_text,
                                    deps=ExtractorAgentDependencies()
                                )
                                
                                # 5. Almacenar en base de datos
                                storage_result = await storage_agent.run(
                                    "store_invoice",
                                    deps=storage_deps,
                                    invoice=extraction_result.data
                                )
                                
                                # 6. Preparar respuesta
                                if storage_result.data.success:
                                    response_message = (
                                        f"✅ Factura procesada correctamente\n"
                                        f"📝 Número: {extraction_result.data.invoice_number}\n"
                                        f"💰 Total: {extraction_result.data.total_amount} {extraction_result.data.currency}\n"
                                        f"🏢 Vendedor: {extraction_result.data.vendor_name}"
                                    )
                                else:
                                    response_message = "❌ Error al procesar la factura. Por favor, intenta nuevamente."
                                
                                await send_whatsapp_message(from_number, response_message)
                                
                            except Exception as e:
                                logging.error(f"Error processing invoice: {str(e)}")
                                await send_whatsapp_message(
                                    from_number,
                                    "❌ Error al procesar la imagen. Por favor, asegúrate de enviar una imagen clara de una factura."
                                )
                        
                        elif message_type == 'text':
                            message_body = message.get('text', {}).get('body', '')
                            logging.info(f'- Body: {message_body}')
                            response_message = "Recibí tu mensaje. Por favor, envía una imagen de una factura para procesarla."
                            await send_whatsapp_message(from_number, response_message)
                        else:
                            logging.info(f'- Full message content: {json.dumps(message, indent=2)}')
                            await send_whatsapp_message(
                                from_number,
                                "❌ Tipo de mensaje no soportado. Por favor, envía una imagen de una factura."
                            )
                            
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
