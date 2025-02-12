import pytest
import requests
from utils import send_whatsapp_message

def test_send_whatsapp_message_success(mock_env_variables, requests_mock):
    """Prueba el envío exitoso de mensajes"""
    # Mock la respuesta de la API
    api_response = {'message_id': 'test_id'}
    requests_mock.post(
        f"https://graph.facebook.com/v18.0/{mock_env_variables['WHATSAPP_PHONE_NUMBER_ID']}/messages",
        json=api_response
    )
    
    response = send_whatsapp_message('+1234567890', 'Test message')
    assert response == api_response

def test_send_whatsapp_message_invalid_phone(mock_env_variables):
    """Prueba error con número de teléfono inválido"""
    with pytest.raises(ValueError, match="Número de teléfono inválido"):
        send_whatsapp_message('invalid_number', 'Test message')

def test_send_whatsapp_message_empty_message(mock_env_variables):
    """Prueba error con mensaje vacío"""
    with pytest.raises(ValueError, match="El mensaje no puede estar vacío"):
        send_whatsapp_message('+1234567890', '')

def test_send_whatsapp_message_api_error(mock_env_variables, requests_mock):
    """Prueba error en la API de WhatsApp"""
    requests_mock.post(
        f"https://graph.facebook.com/v18.0/{mock_env_variables['WHATSAPP_PHONE_NUMBER_ID']}/messages",
        status_code=400,
        json={'error': {'message': 'API Error'}}
    )
    
    with pytest.raises(requests.exceptions.HTTPError):
        send_whatsapp_message('+1234567890', 'Test message')