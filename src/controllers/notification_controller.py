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
            print("🔍 GET /notifications/ - Procesando petición")
            
            current_user = get_current_user()
            if not current_user or not current_user.get('user_id'):
                print("❌ Usuario no autenticado correctamente")
                return jsonify({
                    'success': False,
                    'error': 'Usuario no autenticado',
                    'data': None
                }), 401
            
            user_id = current_user.get('user_id')
            print(f"🔑 Usuario autenticado: {user_id}")
            
            # Obtener parámetros de consulta
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            unread_only = request.args.get('unread_only', 'false').lower() == 'true'
            
            print(f"📊 Parámetros: page={page}, per_page={per_page}, unread_only={unread_only}")
            
            # Validar parámetros
            if page < 1:
                return jsonify({
                    'success': False,
                    'error': 'El número de página debe ser mayor a 0',
                    'data': None
                }), 400
            if per_page < 1 or per_page > 100:
                return jsonify({
                    'success': False,
                    'error': 'Los elementos por página deben estar entre 1 y 100',
                    'data': None
                }), 400
            
            # Obtener notificaciones
            print(f"🔄 Llamando al servicio con user_id: {user_id}")
            result = notification_service.get_user_notifications(
                user_id=user_id,
                page=page,
                per_page=per_page,
                unread_only=unread_only
            )
            
            print(f"📊 Resultado del servicio: Total notificaciones={len(result.get('notifications', []))}")
            
            # Verificar el contenido de las notificaciones
            notifications = result.get('notifications', [])
            if notifications:
                print(f"📋 Primera notificación ID: {notifications[0].get('id', 'Sin ID')}")
            else:
                print("⚠️ Lista de notificaciones está vacía")
            
            # Crear respuesta JSON explícitamente
            response_data = {
                'success': True,
                'data': {
                    'notifications': notifications,
                    'pagination': result.get('pagination', {
                        'page': page,
                        'per_page': per_page,
                        'total': 0,
                        'pages': 0
                    })
                }
            }
            
            print(f"📤 Estructura de respuesta: success={response_data['success']}, notifications_count={len(response_data['data']['notifications'])}")
            
            # Verificar que la respuesta sea JSON serializable
            try:
                import json
                json_test = json.dumps(response_data)
                print("✅ Respuesta es JSON serializable")
            except Exception as e:
                print(f"❌ Error de serialización JSON: {e}")
                print(f"❌ Tipo problemático: {type(e)}")
                # Si hay error, devolver respuesta simplificada
                return jsonify({
                    'success': True,
                    'data': {
                        'notifications': [],
                        'pagination': response_data['data']['pagination']
                    }
                }), 200
            
            # Usar Response de Flask puro para evitar problemas de serialización de Flask-RESTX
            from flask import Response
            
            json_response = json.dumps(response_data, ensure_ascii=False, indent=2)
            return Response(
                json_response,
                status=200,
                mimetype='application/json',
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            
        except NotificationServiceError as e:
            print(f"❌ Error del servicio: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'data': None
            }), 400
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'data': None
            }), 500
    
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
            
            return {
                'success': True,
                'message': f'{count} notificaciones marcadas como leídas'
            }, 200
            
        except NotificationServiceError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Error interno del servidor'}, 500
    
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
            print("🔔 Webhook create_notification - Iniciando")
            
            data = request.get_json()
            print(f"📨 Datos recibidos: {data}")
            
            # Validar datos requeridos
            if not data or not all(key in data for key in ['report_id', 'response_id', 'response_data']):
                print("❌ Datos faltantes en webhook")
                return jsonify({'error': 'Datos requeridos: report_id, response_id, response_data'}), 400
            
            print(f"📊 Report ID: {data['report_id']}")
            print(f"📊 Response ID: {data['response_id']}")
            print(f"📊 Response Data: {data['response_data']}")
            
            # Crear notificación
            print("🔄 Llamando al servicio de notificaciones...")
            notification = notification_service.create_notification(
                report_id=data['report_id'],
                response_id=data['response_id'],
                response_data=data['response_data']
            )
            
            print(f"✅ Notificación creada: {notification.id}")
            
            # Convertir a diccionario manualmente
            notification_dict = {
                'id': str(notification.id),
                'user_id': notification.user_id,
                'report_id': notification.report_id,
                'response_id': notification.response_id,
                'notification_type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat() if hasattr(notification.created_at, 'isoformat') else str(notification.created_at)
            }
            
            print(f"📤 Devolviendo respuesta: {notification_dict}")
            
            return jsonify({
                'success': True,
                'message': 'Notificación creada exitosamente',
                'data': notification_dict
            }), 201
            
        except NotificationServiceError as e:
            print(f"❌ Error del servicio: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            print(f"❌ Tipo de error: {type(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
