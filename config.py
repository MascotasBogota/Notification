import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'patitas-bog-secret-key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/patitas-bog'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'patitas-bog-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Configuración del servidor
    PORT = int(os.environ.get('PORT', 5010))
    
    # Configuración de notificaciones
    NOTIFICATIONS_PER_PAGE = 10
    MAX_NOTIFICATION_AGE_DAYS = 30

class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/patitas-bog-dev'

class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    MONGO_URI = os.environ.get('MONGO_URI')

class TestingConfig(Config):
    """Configuración para pruebas."""
    TESTING = True
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/patitas-bog-test'

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
