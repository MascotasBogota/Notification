import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'patitas-bog-secret-key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/patitas-bog'
    
    # JWT - CORREGIR: usar la misma variable que LogIn_backend
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.environ.get('JWT_SECRET') or 'patitas-bog-jwt-secret'
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
    
    @staticmethod
    def init_app(app):
        """Inicializar configuración de desarrollo con debug"""
        # Debug de configuración JWT
        jwt_secret = os.environ.get('JWT_SECRET_KEY') or os.environ.get('JWT_SECRET')
        print(f"🔑 JWT_SECRET configurado: {'✅' if jwt_secret else '❌'}")
        if jwt_secret:
            print(f"   Longitud: {len(jwt_secret)} caracteres")
            print(f"   Primeros caracteres: {jwt_secret[:10]}...")
        
        # Debug de MongoDB
        mongo_uri = os.environ.get('MONGO_URI')
        print(f"🔗 MongoDB configurado: {'✅' if mongo_uri else '❌'}")
        if mongo_uri:
            # Ocultar password en log
            safe_uri = mongo_uri.split('@')[1] if '@' in mongo_uri else mongo_uri
            print(f"   Host: {safe_uri}")
        
        print(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'not_set')}")
        print(f"🚀 Port: {Config.PORT}")
        print("=" * 50)

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
