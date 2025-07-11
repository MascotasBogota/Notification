from flask_restx import Namespace, Resource, fields
from src.controllers.notification_controller import NotificationController

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
    @ns.doc('get_user_notifications')
    @ns.param('page', 'Número de página', type=int, default=1)
    @ns.param('per_page', 'Elementos por página', type=int, default=10)
    @ns.param('unread_only', 'Solo notificaciones no leídas', type=bool, default=False)
    @ns.marshal_with(notifications_response_model)
    @ns.response(200, 'Notificaciones obtenidas exitosamente')
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
    @ns.doc('get_notification')
    @ns.marshal_with(ns.model('SingleNotificationResponse', {
        'success': fields.Boolean(required=True),
        'data': fields.Nested(notification_model)
    }))
    @ns.response(200, 'Notificación obtenida exitosamente')
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
    @ns.doc('mark_notification_as_read')
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
    @ns.doc('mark_all_notifications_as_read')
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
    @ns.doc('get_unread_count')
    @ns.marshal_with(unread_count_model)
    @ns.response(200, 'Conteo obtenido exitosamente')
    @ns.response(401, 'Token requerido o inválido')
    @ns.response(500, 'Error interno del servidor')
    def get(self):
        """
        Obtener el número de notificaciones no leídas del usuario
        
        Retorna el conteo de notificaciones que el usuario aún no ha leído.
        Útil para mostrar badges o indicadores en la interfaz.
        """
        return NotificationController.get_unread_count()
