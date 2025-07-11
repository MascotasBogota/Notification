import pytest
from mongoengine import connect, disconnect
from app import create_app
from config import TestingConfig

@pytest.fixture
def app():
    """Fixture para crear la aplicación Flask de testing"""
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Fixture para crear el cliente de testing"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture para crear el runner de comandos CLI"""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def mongo_mock():
    """Fixture para mockear MongoDB"""
    # Conectar a base de datos de test
    connect('mongoenginetest', host='mongomock://localhost')
    yield
    # Desconectar después del test
    disconnect()

@pytest.fixture
def mock_jwt_token():
    """Fixture para generar un token JWT mock"""
    import jwt
    import os
    
    payload = {
        'user_id': 'test_user_123',
        'email': 'test@example.com',
        'exp': 9999999999  # Token que no expira para tests
    }
    
    secret_key = os.getenv('JWT_SECRET_KEY', 'patitas-bog-jwt-secret')
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    return token

@pytest.fixture
def auth_headers(mock_jwt_token):
    """Fixture para headers de autenticación"""
    return {
        'Authorization': f'Bearer {mock_jwt_token}',
        'Content-Type': 'application/json'
    }
