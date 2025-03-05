import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.config import settings
from main import app
from models.invoice import Invoice
from agents.vision_agent import VisionResult
from agents.storage_agent import StorageResult

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_whatsapp_message_data():
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+1234567890",
                                "phone_number_id": "1234567890"
                            },
                            "messages": [
                                {
                                    "from": "1234567890",
                                    "timestamp": "1636826349",
                                    "type": "text",
                                    "text": {
                                        "body": "Hello"
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def mock_whatsapp_image_data():
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+1234567890",
                                "phone_number_id": "1234567890"
                            },
                            "messages": [
                                {
                                    "from": "1234567890",
                                    "timestamp": "1636826349",
                                    "type": "image",
                                    "image": {
                                        "id": "123456789",
                                        "mime_type": "image/jpeg"
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

def test_webhook_verification_success(client):
    """Prueba la verificaciu00f3n exitosa del webhook"""
    challenge = "challenge_string"
    
    response = client.get(
        f"/webhook/?hub.mode=subscribe&hub.verify_token={settings.WHATSAPP_VERIFY_TOKEN_WEBHOOK}&hub.challenge={challenge}"
    )
    
    assert response.status_code == 200
    assert response.text == challenge

def test_webhook_verification_failure(client):
    """Prueba la verificaciu00f3n fallida del webhook con token incorrecto"""
    challenge = "challenge_string"
    
    response = client.get(
        f"/webhook/?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge={challenge}"
    )
    
    assert response.status_code == 403

def test_receive_text_message(client, mock_whatsapp_message_data):
    """Prueba la recepcciu00f3n de mensajes de texto"""
    with patch('utils.send_whatsapp_message', new_callable=AsyncMock) as mock_send_message:
        response = client.post(
            "/webhook/",
            content=json.dumps(mock_whatsapp_message_data),
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        mock_send_message.assert_called_once()

@pytest.mark.asyncio
async def test_process_image(mock_whatsapp_image_data):
    """Prueba el procesamiento completo de una imagen de factura"""
    # Preparar mocks
    with patch('utils.get_image_from_whatsapp', new_callable=AsyncMock) as mock_get_image, \
         patch('agents.vision_agent.vision_agent.run', new_callable=AsyncMock) as mock_vision_agent, \
         patch('agents.data_extraction_agent.extraction_agent.run', new_callable=AsyncMock) as mock_extraction_agent, \
         patch('agents.storage_agent.storage_agent.run', new_callable=AsyncMock) as mock_storage_agent, \
         patch('utils.send_whatsapp_message', new_callable=AsyncMock) as mock_send_message:
        
        # Configurar los mocks
        mock_get_image.return_value = b'fake_image_data'
        
        # Mock para vision_agent
        vision_mock = MagicMock()
        vision_mock.data = VisionResult(
            extracted_text="Factura #123 de Empresa XYZ por $100",
            confidence=0.95,
            provider="openai",
            model="gpt-4-vision-preview"
        )
        mock_vision_agent.return_value = vision_mock
        
        # Mock para extraction_agent
        extraction_mock = MagicMock()
        extraction_mock.data = Invoice(
            invoice_number="123",
            date="2024-03-04T00:00:00",
            vendor_name="Empresa XYZ",
            vendor_tax_id="123456789",
            total_amount=100.0,
            tax_amount=10.0,
            items=[{
                "description": "Servicio",
                "quantity": 1,
                "unit_price": 90.0,
                "total": 90.0
            }],
            currency="USD"
        )
        mock_extraction_agent.return_value = extraction_mock
        
        # Mock para storage_agent
        storage_mock = MagicMock()
        storage_mock.data = StorageResult(
            invoice_id="123",
            success=True,
            message="Factura almacenada correctamente"
        )
        mock_storage_agent.return_value = storage_mock
        
        # Ejecutar el endpoint con TestClient
        with TestClient(app) as client:
            response = client.post(
                "/webhook/",
                content=json.dumps(mock_whatsapp_image_data),
                headers={"Content-Type": "application/json"}
            )
        
        # Verificar que todos los mocks se llamaron correctamente
        assert response.status_code == 200
        mock_get_image.assert_called_once()
        mock_vision_agent.assert_called_once()
        mock_extraction_agent.assert_called_once()
        mock_storage_agent.assert_called_once()
        mock_send_message.assert_called_once()
