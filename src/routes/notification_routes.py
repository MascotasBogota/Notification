from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from src.controllers.notification_controller import NotificationController
import os

# Namespace para las notificaciones
ns = Namespace('notifications', description='Operaciones relacionadas con notificaciones de avistamientos')

# Modelos para la documentación de Swagger
notification_model = ns.model('Notification', {
    'id': fields.String(required=True, description='ID de la notificación'),
    'user_id': fields.String(required=True, description='ID del usuario que recibe la notificación'),
    'report_id': fields.String(required=True, description='ID del reporte de mascota perdida'),
    'response_id': fields.String(required=True, description='ID del avistamiento/respuesta'),
    'notification_type': fields.String(required=True, description='Tipo de notificación', enum=['avistamiento', 'hallazgo']),
    'title': fields.String(required=True, description='Título de la notificación'),
    'message': fields.String(required=True, description='Mensaje de la notificación'),
    'sighting_data': fields.Nested(ns.model('SightingData', {
        'description': fields.String(description='Descripción del avistamiento'),
        'location': fields.List(fields.Float, description='Coordenadas [longitud, latitud]'),
        'images': fields.List(fields.String, description='URLs de las imágenes'),
        'sighting_time': fields.DateTime(description='Fecha y hora del avistamiento')
    })),
    'is_read': fields.Boolean(required=True, description='Estado de lectura'),
    'created_at': fields.DateTime(required=True, description='Fecha de creación'),
    'read_at': fields.DateTime(description='Fecha de lectura')
})

notifications_response_model = ns.model('NotificationsResponse', {
    'success': fields.Boolean(required=True, description='Éxito de la operación'),
    'data': fields.Nested(ns.model('NotificationsData', {
        'notifications': fields.List(fields.Nested(notification_model)),
        'pagination': fields.Nested(ns.model('Pagination', {
            'page': fields.Integer(description='Página actual'),
            'per_page': fields.Integer(description='Elementos por página'),
            'total': fields.Integer(description='Total de elementos'),
            'pages': fields.Integer(description='Total de páginas')
        }))
    }))
})

create_notification_model = ns.model('CreateNotification', {
    'report_id': fields.String(required=True, description='ID del reporte'),
    'response_id': fields.String(required=True, description='ID de la respuesta/avistamiento'),
    'response_data': fields.Nested(ns.model('ResponseData', {
        'type': fields.String(required=True, description='Tipo de respuesta', enum=['avistamiento', 'hallazgo']),
        'comment': fields.String(required=True, description='Descripción del avistamiento'),
        'location': fields.List(fields.Float, description='Coordenadas [longitud, latitud]'),
        'images': fields.List(fields.String, description='URLs de las imágenes'),
        'created_at': fields.DateTime(description='Fecha y hora del avistamiento')
    }))
})

unread_count_model = ns.model('UnreadCount', {
    'success': fields.Boolean(required=True, description='Éxito de la operación'),
    'data': fields.Nested(ns.model('UnreadCountData', {
        'unread_count': fields.Integer(description='Número de notificaciones no leídas')
    }))
})

@ns.route('/')
class NotificationList(Resource):
    @ns.doc('get_user_notifications', security='Bearer Auth')
    @ns.param('page', 'Número de página', type=int, default=1)
    @ns.param('per_page', 'Elementos por página', type=int, default=10)
    @ns.param('unread_only', 'Solo notificaciones no leídas', type=bool, default=False)
    @ns.response(200, 'Notificaciones obtenidas exitosamente', notifications_response_model)
    @ns.response(400, 'Parámetros inválidos')
    @ns.response(401, 'Token requerido o inválido')
    @ns.response(500, 'Error interno del servidor')
    def get(self):
        """
        Obtener notificaciones del usuario actual
        
        Retorna una lista paginada de notificaciones del usuario autenticado.
        Se pueden filtrar para mostrar solo las no leídas.
        """
        return NotificationController.get_user_notifications()

@ns.route('/webhook')
class NotificationWebhook(Resource):
    @ns.doc('create_notification')
    @ns.expect(create_notification_model)
    @ns.response(201, 'Notificación creada exitosamente')
    @ns.response(400, 'Datos inválidos')
    @ns.response(500, 'Error interno del servidor')
    def post(self):
        """
        Crear una nueva notificación (webhook para otros servicios)
        
        Este endpoint es utilizado por otros servicios para crear notificaciones
        cuando se registra un nuevo avistamiento en un reporte.
        """
        return NotificationController.create_notification()

@ns.route('/<string:notification_id>')
class NotificationResource(Resource):
    @ns.doc('get_notification', security='Bearer Auth')
    @ns.response(200, 'Notificación obtenida exitosamente', ns.model('SingleNotificationResponse', {
        'success': fields.Boolean(required=True),
        'data': fields.Nested(notification_model)
    }))
    @ns.response(404, 'Notificación no encontrada')
    @ns.response(401, 'Token requerido o inválido')
    @ns.response(500, 'Error interno del servidor')
    def get(self, notification_id):
        """
        Obtener una notificación específica por ID
        
        Retorna los detalles completos de una notificación, incluyendo
        la información del avistamiento sin datos personales del usuario
        que reportó el avistamiento.
        """
        return NotificationController.get_notification_by_id(notification_id)

@ns.route('/<string:notification_id>/read')
class NotificationRead(Resource):
    @ns.doc('mark_notification_as_read', security='Bearer Auth')
    @ns.response(200, 'Notificación marcada como leída')
    @ns.response(404, 'Notificación no encontrada')
    @ns.response(401, 'Token requerido o inválido')
    @ns.response(500, 'Error interno del servidor')
    def patch(self, notification_id):
        """
        Marcar una notificación como leída
        
        Actualiza el estado de la notificación a leída y registra
        la fecha y hora de lectura.
        """
        return NotificationController.mark_notification_as_read(notification_id)

@ns.route('/read-all')
class NotificationReadAll(Resource):
    @ns.doc('mark_all_notifications_as_read', security='Bearer Auth')
    @ns.response(200, 'Todas las notificaciones marcadas como leídas')
    @ns.response(401, 'Token requerido o inválido')
    @ns.response(500, 'Error interno del servidor')
    def patch(self):
        """
        Marcar todas las notificaciones del usuario como leídas
        
        Actualiza el estado de todas las notificaciones no leídas
        del usuario a leídas.
        """
        return NotificationController.mark_all_notifications_as_read()

@ns.route('/unread-count')
class NotificationUnreadCount(Resource):
    @ns.doc('get_unread_count', security='Bearer Auth')
    @ns.response(200, 'Conteo obtenido exitosamente', unread_count_model)
    @ns.response(401, 'Token requerido o inválido')
    @ns.response(500, 'Error interno del servidor')
    def get(self):
        """
        Obtener el número de notificaciones no leídas del usuario
        
        Retorna el conteo de notificaciones que el usuario aún no ha leído.
        Útil para mostrar badges o indicadores en la interfaz.
        """
        return NotificationController.get_unread_count()

@ns.route('/debug/jwt')
class JWTDebug(Resource):
    @ns.doc('debug_jwt', description='Debug de configuración JWT')
    def get(self):
        """Endpoint de debug para verificar configuración JWT"""
        auth_header = request.headers.get('Authorization')
        
        debug_info = {
            'jwt_secret_configured': bool(os.environ.get('JWT_SECRET_KEY')),
            'jwt_secret_length': len(os.environ.get('JWT_SECRET_KEY', '')),
            'auth_header_present': bool(auth_header),
            'auth_header_format': 'Bearer token' if auth_header and auth_header.startswith('Bearer ') else 'Invalid or missing',
            'environment': os.environ.get('FLASK_ENV', 'not_set'),
            'token_length': len(auth_header.replace('Bearer ', '')) if auth_header and auth_header.startswith('Bearer ') else 0
        }
        
        return {
            'message': 'JWT Debug Information',
            'debug': debug_info
        }, 200

@ns.route('/debug/jwt-validate')
class JWTValidate(Resource):
    @ns.doc('validate_jwt', description='Validar JWT token')
    def get(self):
        """Validar JWT token y mostrar información"""
        try:
            # Intentar verificar JWT
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            jwt_claims = get_jwt()
            
            return {
                'message': 'JWT válido',
                'user_id': user_id,
                'jwt_claims': {
                    'exp': jwt_claims.get('exp'),
                    'iat': jwt_claims.get('iat'),
                    'sub': jwt_claims.get('sub'),
                    'type': jwt_claims.get('type')
                }
            }, 200
            
        except Exception as e:
            return {
                'message': 'JWT inválido',
                'error': str(e),
                'error_type': type(e).__name__
            }, 401

@ns.route('/debug/create-test-token')
class CreateTestToken(Resource):
    @ns.doc('create_test_token', description='Crear token de prueba (solo para desarrollo)')
    def post(self):
        """Crear un token JWT de prueba para testing"""
        try:
            from flask_jwt_extended import create_access_token
            from datetime import timedelta
            
            # Crear token para usuario de prueba
            test_user_id = "test_user_123"
            token = create_access_token(
                identity=test_user_id,
                expires_delta=timedelta(hours=1)
            )
            
            return {
                'message': 'Token de prueba creado',
                'token': token,
                'user_id': test_user_id,
                'expires_in': '1 hour',
                'usage': f'Bearer {token}'
            }, 200
            
        except Exception as e:
            return {
                'message': 'Error creando token',
                'error': str(e)
            }, 500

@ns.route('/debug/request-headers')
class RequestHeadersDebug(Resource):
    @ns.doc('debug_request_headers')
    def get(self):
        """Debug: Mostrar todos los headers de la petición"""
        headers_dict = dict(request.headers)
        
        return {
            'message': 'Headers de la petición',
            'headers': headers_dict,
            'authorization_header': request.headers.get('Authorization'),
            'method': request.method,
            'url': request.url,
            'path': request.path,
            'query_params': dict(request.args),
            'user_agent': request.headers.get('User-Agent'),
            'content_type': request.headers.get('Content-Type')
        }
