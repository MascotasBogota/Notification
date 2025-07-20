from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from src.extensions import api, init_db, jwt
from src.routes.notification_routes import ns as notifications_ns
import os

# Importar telemetría de forma opcional
try:
    from src.utils.telemetry import init_telemetry
    TELEMETRY_AVAILABLE = True
except ImportError as e:
    TELEMETRY_AVAILABLE = False
    print("⚠️  Telemetría no disponible - continuando sin telemetría")
    print(f"   Error: {str(e)}")

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)  # Habilita CORS para la aplicación

    # Inicializar configuración con debug
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)

    # Inicializar JWT
    jwt.init_app(app)

    # Inicializa base de datos y API Swagger
    init_db(app)
    
    # Inicializar telemetría solo si está disponible
    if TELEMETRY_AVAILABLE:
        try:
            init_telemetry(app)
            print("✅ Telemetría inicializada correctamente")
        except Exception as e:
            print(f"⚠️  Error inicializando telemetría: {str(e)}")
    
    api.init_app(app)

    # Registra los endpoints de /notifications
    api.add_namespace(notifications_ns, path="/notifications")
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'PatitasBog Notifications API',
            'version': '1.0.0'
        }, 200
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 5010))
    print(f"🚀 Iniciando servicio en http://localhost:{port}")
    print(f"📚 Documentación: http://localhost:{port}/docs/")
    print(f"🩺 Health check: http://localhost:{port}/health")
    app.run(host="0.0.0.0", port=port, debug=True)
