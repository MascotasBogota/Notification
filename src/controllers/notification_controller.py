from flask import request, jsonify
from src.services.notification_service import notification_service, NotificationServiceError
from src.utils.auth import jwt_required, get_current_user

class NotificationController:
    """Controlador para gestionar notificaciones"""
    
    @staticmethod
    @jwt_required
    def get_user_notifications():
        """
        Obtener notificaciones del usuario actual
        
        Query params:
        - page: número de página (default: 1)
        - per_page: elementos por página (default: 10)
        - unread_only: solo notificaciones no leídas (default: false)
        """
        try:
            current_user = get_current_user()
            user_id = current_user.get('user_id')
            
            # Obtener parámetros de consulta
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            unread_only = request.args.get('unread_only', 'false').lower() == 'true'
            
            # Validar parámetros
            if page < 1:
                return jsonify({'error': 'El número de página debe ser mayor a 0'}), 400
            if per_page < 1 or per_page > 100:
                return jsonify({'error': 'Los elementos por página deben estar entre 1 y 100'}), 400
            
            # Obtener notificaciones
            result = notification_service.get_user_notifications(
                user_id=user_id,
                page=page,
                per_page=per_page,
                unread_only=unread_only
            )
            
            return jsonify({
                'success': True,
                'data': result
            }), 200
            
        except NotificationServiceError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    @staticmethod
    @jwt_required
    def get_notification_by_id(notification_id):
        """
        Obtener una notificación específica por ID
        
        Args:
            notification_id: ID de la notificación
        """
        try:
            current_user = get_current_user()
            user_id = current_user.get('user_id')
            
            # Obtener notificación
            notification = notification_service.get_notification_by_id(notification_id, user_id)
            
            if not notification:
                return jsonify({'error': 'Notificación no encontrada'}), 404
            
            return jsonify({
                'success': True,
                'data': notification.to_dict()
            }), 200
            
        except NotificationServiceError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    @staticmethod
    @jwt_required
    def mark_notification_as_read(notification_id):
        """
        Marcar una notificación como leída
        
        Args:
            notification_id: ID de la notificación
        """
        try:
            current_user = get_current_user()
            user_id = current_user.get('user_id')
            
            # Marcar como leída
            success = notification_service.mark_notification_as_read(notification_id, user_id)
            
            if not success:
                return jsonify({'error': 'Notificación no encontrada'}), 404
            
            return jsonify({
                'success': True,
                'message': 'Notificación marcada como leída'
            }), 200
            
        except NotificationServiceError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    @staticmethod
    @jwt_required
    def mark_all_notifications_as_read():
        """
        Marcar todas las notificaciones del usuario como leídas
        """
        try:
            current_user = get_current_user()
            user_id = current_user.get('user_id')
            
            # Marcar todas como leídas
            count = notification_service.mark_all_notifications_as_read(user_id)
            
            return jsonify({
                'success': True,
                'message': f'{count} notificaciones marcadas como leídas'
            }), 200
            
        except NotificationServiceError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    @staticmethod
    @jwt_required
    def get_unread_count():
        """
        Obtener el número de notificaciones no leídas del usuario
        """
        try:
            current_user = get_current_user()
            user_id = current_user.get('user_id')
            
            # Obtener conteo
            count = notification_service.get_unread_count(user_id)
            
            return jsonify({
                'success': True,
                'data': {
                    'unread_count': count
                }
            }), 200
            
        except NotificationServiceError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    @staticmethod
    def create_notification():
        """
        Crear una nueva notificación (webhook para otros servicios)
        
        Body:
        {
            "report_id": "string",
            "response_id": "string",
            "response_data": {
                "type": "avistamiento|hallazgo",
                "comment": "string",
                "location": [longitude, latitude],
                "images": ["url1", "url2"],
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
        """
        try:
            data = request.get_json()
            
            # Validar datos requeridos
            if not data or not all(key in data for key in ['report_id', 'response_id', 'response_data']):
                return jsonify({'error': 'Datos requeridos: report_id, response_id, response_data'}), 400
            
            # Crear notificación
            notification = notification_service.create_notification(
                report_id=data['report_id'],
                response_id=data['response_id'],
                response_data=data['response_data']
            )
            
            return jsonify({
                'success': True,
                'message': 'Notificación creada exitosamente',
                'data': notification.to_dict()
            }), 201
            
        except NotificationServiceError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
