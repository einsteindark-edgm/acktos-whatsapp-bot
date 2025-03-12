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

async def process_image(message: dict, from_number: str, vision_deps, extractor_deps, storage_deps=None) -> dict:
    """
    Procesa una imagen de factura recibida por WhatsApp
    
    Args:
        message: Mensaje recibido con la imagen
        from_number: Número de teléfono del remitente
        vision_deps: Dependencias para el agente de visión
        extractor_deps: Dependencias para el agente de extracción
        storage_deps: Dependencias para almacenamiento (no usado en pruebas)
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        # Notificar al usuario que estamos procesando
        await send_whatsapp_message(
            from_number,
            "Procesando tu imagen... Esto puede tomar unos segundos."
        )
        
        # 1. Obtener la imagen
        logging.info(f"Obteniendo imagen de WhatsApp de: {from_number}")
        image_data = await get_image_from_whatsapp(message)
        logging.info(f"Imagen recibida: {len(image_data)} bytes")
        
        # 2. Procesar con Vision Agent
        logging.info("Iniciando extracción de texto con Vision Agent")
        
        try:
            # Agregar la imagen a las dependencias
            logging.info(f"Tamaño de la imagen: {len(image_data)} bytes")
            
            # Verificar que vision_deps tenga los valores correctos antes de la llamada
            logging.info(f"Vision provider: {vision_deps.vision_provider.__class__.__name__}")
            logging.info(f"Model name: {vision_deps.model_name}")
            logging.info(f"API key configurada: {bool(vision_deps.api_key)}")
            
            # Crear un objeto de dependencias con la imagen incluida
            vision_deps.image_data = image_data
            logging.info("Imagen agregada a las dependencias correctamente")
            
            # Llamar al vision_agent con un prompt simple, el agente usará la herramienta process_invoice_image
            logging.info("Iniciando llamada a vision_agent.run()...")
            vision_result = await vision_agent.run(
                "Procesa esta imagen de factura y extrae todo su texto",
                deps=vision_deps
            )
            
            logging.info("Vision agent ejecutado correctamente")
        except Exception as e:
            logging.error(f"Error en vision_agent: {str(e)}")
            raise
        logging.info(f"Texto extraído: {len(vision_result.data.extracted_text)} caracteres")
        
        # 3. Extraer datos estructurados
        logging.info("Extrayendo datos estructurados")
        extraction_result = await extraction_agent.run(
            vision_result.data.extracted_text,
            deps=extractor_deps
        )
        invoice = extraction_result.data
        logging.info(f"Datos estructurados extraidos: {invoice}")
        
        # 4. Preparar respuesta
        response_message = (
            "✓ Factura procesada correctamente\n" +
            f"- Número: {invoice.invoice_number}\n" +
            f"- Total: {invoice.total_amount} {invoice.currency}\n" +
            f"- Vendedor: {invoice.vendor_name}"
        )
        
        # 5. Enviar respuesta a WhatsApp
        logging.info(f"Enviando resultado al usuario: {from_number}")
        await send_whatsapp_message(from_number, response_message)
        
        return {
            "status": "success",
            "extracted_data": {
                "invoice_number": invoice.invoice_number,
                "total_amount": invoice.total_amount,
                "currency": invoice.currency,
                "vendor_name": invoice.vendor_name
            }
        }
        
    except Exception as e:
        error_msg = f"Error al procesar la imagen: {str(e)}"
        logging.error(error_msg)
        
        # Notificar al usuario del error
        await send_whatsapp_message(
            from_number,
            "✗ Error al procesar la imagen. Por favor, asegúrate de enviar una imagen clara de una factura."
        )
        
        return {
            "status": "error",
            "message": str(e)
        }
