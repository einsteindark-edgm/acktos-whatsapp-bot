import pytest
import json
import os

# Mock de Azure Functions para testing
class MockHttpRequest:
    def __init__(self, method='GET', url='https://test.com/api/webhook', params=None, body=None, headers=None):
        self.method = method
        self.url = url
        self.params = params or {}
        self.body = body
        self.headers = headers or {}
        
    def get_body(self):
        return self.body if self.body else b''
        
    def get_json(self):
        if not self.body:
            return {}
        return json.loads(self.body.decode('utf-8'))

class MockHttpResponse:
    def __init__(self, body=None, status_code=200, headers=None):
        self.body = body
        self.status_code = status_code
        self.headers = headers or {}

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
    """Fixture para la aplicación de prueba"""
    # Retorna un objeto que simule el comportamiento necesario para las pruebas
    return {
        'routes': {},
        'handlers': {}
    }

@pytest.fixture
def mock_http_request():
    """Crea un mock de HttpRequest"""
    def _create_request(method='GET', params=None, body=None, headers=None):
        params = params or {}
        headers = headers or {}
        return MockHttpRequest(
            method=method,
            url='https://test.com/api/webhook',
            params=params,
            body=json.dumps(body).encode() if body else None,
            headers=headers
        )
    return _create_request