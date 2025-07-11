from flask import Flask
from flask_cors import CORS
from config import DevelopmentConfig
from src.extensions import api, init_db
from src.routes.notification_routes import ns as notifications_ns

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)  # Habilita CORS para la aplicación

    # Inicializa base de datos y API Swagger
    init_db(app)
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
    create_app().run(host="0.0.0.0", port=5060, debug=True)
