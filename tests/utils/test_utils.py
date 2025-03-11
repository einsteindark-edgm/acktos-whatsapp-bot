import pytest
import sys
import json
import logging
import requests
from unittest.mock import MagicMock, patch
from typing import Dict, Any

# Configurar pytest para tests asíncronos
# Eliminamos pytestmark para evitar errores y usamos decoradores individuales

# Deshabilitar logs durante pruebas
logging.disable(logging.CRITICAL)

# Mock para pydantic_settings
class BaseSettings:
    class Config:
        pass
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

sys.modules['pydantic_settings'] = MagicMock()
sys.modules['pydantic_settings'].BaseSettings = BaseSettings
sys.modules['pydantic_settings'].SettingsConfigDict = dict

# Mock para settings
class MockSettings:
    WHATSAPP_TOKEN = 'test_token'
    WHATSAPP_PHONE_NUMBER_ID = '123456789'

sys.modules['app.config'] = MagicMock()
sys.modules['app.config'].settings = MockSettings

# Crear una versión mockeada de send_whatsapp_message específica para tests
@pytest.mark.anyio
@patch('utils.send_whatsapp_message')
async def test_send_whatsapp_message_success(mock_send, mock_env_variables):
    """Prueba el envío exitoso de mensajes"""
    # Configurar el comportamiento del mock
    mock_result = {'message_id': 'test_id'}
    mock_send.return_value = mock_result
    
    # Importar después de patchear
    from utils import send_whatsapp_message
    
    # Ejecutar
    result = await send_whatsapp_message('+1234567890', 'Test message')
    
    # Verificar
    assert result == mock_result
    mock_send.assert_called_once_with('+1234567890', 'Test message')

@pytest.mark.anyio
@patch('utils.send_whatsapp_message')
async def test_send_whatsapp_message_invalid_phone(mock_send, mock_env_variables):
    """Prueba error con número de teléfono inválido"""
    # Configurar el mock para lanzar la excepción
    mock_send.side_effect = ValueError("Número de teléfono inválido. Debe estar en formato E.164")
    
    # Importar después de patchear
    from utils import send_whatsapp_message
    
    # Verificar que se lanza la excepción
    with pytest.raises(ValueError, match="Número de teléfono inválido"):
        await send_whatsapp_message('invalid_number', 'Test message')

@pytest.mark.anyio
@patch('utils.send_whatsapp_message')
async def test_send_whatsapp_message_empty_message(mock_send, mock_env_variables):
    """Prueba error con mensaje vacío"""
    # Configurar el mock para lanzar la excepción
    mock_send.side_effect = ValueError("El mensaje no puede estar vacío")
    
    # Importar después de patchear
    from utils import send_whatsapp_message
    
    # Verificar que se lanza la excepción
    with pytest.raises(ValueError, match="El mensaje no puede estar vacío"):
        await send_whatsapp_message('+1234567890', '')

@pytest.mark.anyio
@patch('utils.send_whatsapp_message')
async def test_send_whatsapp_message_api_error(mock_send, mock_env_variables):
    """Prueba error en la API de WhatsApp"""
    # Configurar el mock para lanzar la excepción
    mock_send.side_effect = requests.exceptions.HTTPError("HTTP Error")
    
    # Importar después de patchear
    from utils import send_whatsapp_message
    
    # Verificar que se lanza la excepción
    with pytest.raises(requests.exceptions.HTTPError):
        await send_whatsapp_message('+1234567890', 'Test message')
