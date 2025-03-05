import json
import logging
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from typing import Annotated

from app.config import settings
from app.dependencies import get_vision_deps, get_storage_deps, get_extractor_deps
from models.dependencies import VisionAgentDependencies, StorageAgentDependencies, ExtractorAgentDependencies
from utils import send_whatsapp_message, get_image_from_whatsapp
from agents.vision_agent import vision_agent
from agents.data_extraction_agent import extraction_agent
from agents.storage_agent import storage_agent

# Crear el router
router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.get("/")
async def verify_webhook(request: Request):
    """Endpoint para la verificaciu00f3n del webhook de WhatsApp"""
    # Obtener paru00e1metros de la solicitud
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    # Verificar los paru00e1metros
    if not all([mode, token, challenge]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faltan paru00e1metros requeridos"
        )
    
    # Validar el token
    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN_WEBHOOK:
        logging.info(f"Verificaciu00f3n de webhook exitosa")
        return Response(content=challenge)
    else:
        logging.error(f"Fallo en verificaciu00f3n de webhook. Token recibido: {token}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Fallu00f3 la validaciu00f3n. Asegu00farate de que los tokens coincidan."
        )

@router.post("/")
async def receive_message(
    request: Request,
    vision_deps: Annotated[VisionAgentDependencies, Depends(get_vision_deps)],
    storage_deps: Annotated[StorageAgentDependencies, Depends(get_storage_deps)],
    extractor_deps: Annotated[ExtractorAgentDependencies, Depends(get_extractor_deps)]
):
    """Endpoint para recibir mensajes de WhatsApp"""
    try:
        # Obtener el cuerpo de la solicitud
        body_text = await request.body()
        body_text = body_text.decode('utf-8')
        logging.info(f'Raw request body: {body_text}')
        
        # Parsear el JSON
        body = json.loads(body_text)
        logging.info(f"Received webhook data: {json.dumps(body, indent=2)}")
        
        # Validar la estructura del mensaje
        if not body.get("object"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid message format"
            )
        
        # Extraer los mensajes
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
                    # Asegurar que el nu00famero estu00e9 en formato E.164
                    from_number = message.get("from")
                    if from_number and not from_number.startswith("+"):
                        from_number = "+" + from_number
                    logging.info(f"Nu00famero formateado: {from_number}")
                    message_type = message.get("type")
                    
                    logging.info("Message details:")
                    logging.info(f"- From: {from_number}")
                    logging.info(f"- Type: {message_type}")
                    logging.info(f"- Timestamp: {message.get('timestamp')}")
                    
                    # Procesar mensaje segu00fan su tipo
                    if message_type == 'image':
                        await process_image(message, from_number, vision_deps, extractor_deps, storage_deps)
                    elif message_type == 'text':
                        message_body = message.get('text', {}).get('body', '')
                        logging.info(f'- Body: {message_body}')
                        response_message = "Recibu00ed tu mensaje. Por favor, envu00eda una imagen de una factura para procesarla."
                        await send_whatsapp_message(from_number, response_message)
                    else:
                        logging.info(f'- Full message content: {json.dumps(message, indent=2)}')
                        await send_whatsapp_message(
                            from_number,
                            "\u274c Tipo de mensaje no soportado. Por favor, envu00eda una imagen de una factura."
                        )
        
        return {"status": "success"}
    
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

async def process_image(message, from_number, vision_deps, extractor_deps, storage_deps):
    """Procesa una imagen de factura"""
    try:
        # 1. Obtener la imagen
        image_data = await get_image_from_whatsapp(message)
        
        # 2. Procesar la imagen con Vision Agent
        vision_result = await vision_agent.run(
            "Extract text from this invoice",
            deps=vision_deps,
            files={"image": image_data}
        )
        
        # 3. Extraer datos estructurados
        extraction_result = await extraction_agent.run(
            vision_result.data.extracted_text,
            deps=extractor_deps
        )
        
        # 4. Almacenar en base de datos
        storage_result = await storage_agent.run(
            "store_invoice",
            deps=storage_deps,
            invoice=extraction_result.data
        )
        
        # 5. Preparar respuesta
        if storage_result.data.success:
            response_message = (
                f"\u2705 Factura procesada correctamente\n"
                f"\ud83d\udcdd Nu00famero: {extraction_result.data.invoice_number}\n"
                f"\ud83d\udcb0 Total: {extraction_result.data.total_amount} {extraction_result.data.currency}\n"
                f"\ud83c\udfe2 Vendedor: {extraction_result.data.vendor_name}"
            )
        else:
            response_message = "\u274c Error al procesar la factura. Por favor, intenta nuevamente."
        
        await send_whatsapp_message(from_number, response_message)
        
    except Exception as e:
        logging.error(f"Error processing invoice: {str(e)}")
        await send_whatsapp_message(
            from_number,
            "\u274c Error al procesar la imagen. Por favor, asegu00farate de enviar una imagen clara de una factura."
        )
