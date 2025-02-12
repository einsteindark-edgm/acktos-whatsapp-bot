import pytest
import azure.functions as func
import json
import os
from function_app import app

@pytest.fixture
def mock_env_variables(monkeypatch):
    """Configura variables de entorno de prueba"""
    env_vars = {
        'WHATSAPP_TOKEN': 'test_token',
        'WHATSAPP_PHONE_NUMBER_ID': '123456789',
        'WHATSAPP_VERIFY_TOKEN_WEBHOOK': 'test_verify_token'
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars

@pytest.fixture
def mock_app():
    """Fixture para la aplicación de Azure Functions"""
    return app

@pytest.fixture
def mock_http_request():
    """Crea un mock de HttpRequest"""
    def _create_request(method='GET', params=None, body=None, headers=None):
        params = params or {}
        headers = headers or {}
        return func.HttpRequest(
            method=method,
            url='https://test.com/api/webhook',
            params=params,
            body=json.dumps(body).encode() if body else None,
            headers=headers
        )
    return _create_request