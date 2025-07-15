from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from src.extensions import api, init_db, jwt
from src.routes.notification_routes import ns as notifications_ns
from src.utils.telemetry import init_telemetry
import os

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)  # Habilita CORS para la aplicación

    # Inicializar JWT
    jwt.init_app(app)

    # Inicializa base de datos y API Swagger
    init_db(app)
    init_telemetry(app)
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
