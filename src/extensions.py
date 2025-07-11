from flask_restx import Api
from mongoengine import connect

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Agregar "Bearer <token>"'
    }
}

api = Api(   
    title="PatitasBog - Notificaciones API",
    version="1.0",
    description="Servicio de notificaciones para avistamientos de mascotas perdidas",
    authorizations=authorizations,
    doc='/docs/'
)

def init_db(app):
    """
    Initialize the MongoDB connection using the URI from the app's config.
    """
    connect(host=app.config["MONGO_URI"])
