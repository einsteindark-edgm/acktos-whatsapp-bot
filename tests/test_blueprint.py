import pytest
import json
from tests.conftest import MockHttpResponse
from blueprint import handle_webhook, handle_verification, handle_messages

def test_webhook_verification_success(mock_env_variables, mock_http_request):
    """Prueba la verificación exitosa del webhook"""
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': mock_env_variables['WHATSAPP_VERIFY_TOKEN_WEBHOOK'],
        'hub.challenge': 'test_challenge'
    }
    req = mock_http_request(params=params)
    response = handle_webhook(req)
    assert isinstance(response, MockHttpResponse)
    
    assert response.status_code == 200
    assert response.get_body().decode() == 'test_challenge'

def test_webhook_verification_failed_token(mock_env_variables, mock_http_request):
    """Prueba la verificación fallida por token incorrecto"""
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': 'wrong_token',
        'hub.challenge': 'test_challenge'
    }
    req = mock_http_request(params=params)
    response = handle_webhook(req)
    assert isinstance(response, MockHttpResponse)
    
    assert response.status_code == 403

def test_webhook_message_received(mock_env_variables, mock_http_request, mocker):
    """Prueba la recepción de mensajes"""
    # Mock la función send_whatsapp_message
    mock_send = mocker.patch('blueprint.send_whatsapp_message')
    
    body = {
        'object': 'whatsapp_business_account',
        'entry': [{
            'id': 'test_id',
            'changes': [{
                'value': {
                    'messaging_product': 'whatsapp',
                    'metadata': {
                        'display_phone_number': '+1234567890',
                        'phone_number_id': '123456789'
                    },
                    'messages': [{
                        'from': '1234567890',
                        'timestamp': '1675901399',
                        'type': 'text',
                        'text': {
                            'body': 'Test message'
                        }
                    }]
                },
                'field': 'messages'
            }]
        }]
    }
    
    req = mock_http_request(method='POST', body=body)
    response = handle_webhook(req)
    assert isinstance(response, MockHttpResponse)
    
    assert response.status_code == 200
    mock_send.assert_called_once_with(
        '+1234567890',
        'Recibí tu mensaje. Contenido:\nTest message'
    )

def test_webhook_invalid_method(mock_http_request):
    """Prueba método no soportado"""
    req = mock_http_request(method='PUT')
    response = handle_webhook(req)
    assert isinstance(response, MockHttpResponse)
    
    assert response.status_code == 405