import pytest
from mongoengine import connect, disconnect
from app import create_app
from config import TestingConfig
import jwt as jwt_lib

@pytest.fixture
def app():
    """Fixture para crear la aplicación Flask de testing"""
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
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
    try:
        connect('mongoenginetest', host='mongomock://localhost')
        yield
        # Desconectar después del test
        disconnect()
    except:
        # Si mongomock no está disponible, usar conexión normal
        yield

@pytest.fixture
def mock_jwt_token():
    """Fixture para generar un token JWT mock"""
    payload = {
        'sub': 'test_user_123',  # Usar 'sub' en lugar de 'user_id'
        'email': 'test@example.com',
        'exp': 9999999999  # Token que no expira para tests
    }
    
    secret_key = 'test-secret-key'
    token = jwt_lib.encode(payload, secret_key, algorithm='HS256')
    
    return token

@pytest.fixture
def auth_headers(mock_jwt_token):
    """Fixture para headers de autenticación"""
    return {
        'Authorization': f'Bearer {mock_jwt_token}',
        'Content-Type': 'application/json'
    }
