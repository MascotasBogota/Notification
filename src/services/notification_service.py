from src.models.notification_model import Notification
from mongoengine import DoesNotExist
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import os

class NotificationServiceError(Exception):
    """Excepción personalizada para errores del servicio de notificaciones"""
    pass

class NotificationService:
    """Servicio para gestionar notificaciones de avistamientos"""
    
    def __init__(self):
        # URLs de otros servicios
        self.reports_service_url = os.getenv('REPORTS_SERVICE_URL', 'http://localhost:5050')
        self.users_service_url = os.getenv('USERS_SERVICE_URL', 'http://localhost:5000')
    
    def create_notification(self, report_id: str, response_id: str, response_data: Dict) -> Notification:
        """
        Crear una notificación cuando se registra un nuevo avistamiento
        
        Args:
            report_id: ID del reporte
            response_id: ID de la respuesta/avistamiento
            response_data: Datos de la respuesta que incluyen:
                - type: tipo de respuesta (avistamiento/hallazgo)
                - comment: descripción del avistamiento
                - location: ubicación del avistamiento
                - images: lista de URLs de imágenes
                - created_at: fecha y hora del avistamiento
        
        Returns:
            Notification: La notificación creada
        """
        try:
            # Obtener información del reporte para saber a quién notificar
            report_owner_id = self._get_report_owner(report_id)
            
            # Crear título y mensaje apropiados
            notification_type = response_data.get('type', 'avistamiento')
            title = f"Nuevo {notification_type}"
            message = f"Se ha registrado un nuevo {notification_type} para tu reporte de mascota perdida"
            
            # Crear la notificación
            notification = Notification(
                user_id=report_owner_id,
                report_id=report_id,
                response_id=response_id,
                notification_type=notification_type,
                title=title,
                message=message,
                sighting_data={
                    'description': response_data.get('comment'),
                    'location': response_data.get('location'),
                    'images': response_data.get('images', []),
                    'sighting_time': response_data.get('created_at', datetime.utcnow())
                }
            )
            
            notification.save()
            return notification
            
        except Exception as e:
            raise NotificationServiceError(f"Error al crear notificación: {str(e)}")
    
    def get_user_notifications(self, user_id: str, page: int = 1, per_page: int = 10, 
                              unread_only: bool = False) -> Dict:
        """
        Obtener notificaciones de un usuario
        
        Args:
            user_id: ID del usuario
            page: Página para paginación
            per_page: Elementos por página
            unread_only: Solo notificaciones no leídas
            
        Returns:
            Dict con las notificaciones y metadata de paginación
        """
        try:
            # Construir query
            query = {'user_id': user_id}
            if unread_only:
                query['is_read'] = False
            
            # Obtener total de notificaciones
            total = Notification.objects(**query).count()
            
            # Obtener notificaciones paginadas
            notifications = Notification.objects(**query)\
                .order_by('-created_at')\
                .skip((page - 1) * per_page)\
                .limit(per_page)
            
            # Convertir a diccionarios
            notifications_data = [notification.to_dict() for notification in notifications]
            
            return {
                'notifications': notifications_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            raise NotificationServiceError(f"Error al obtener notificaciones: {str(e)}")
    
    def get_notification_by_id(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """
        Obtener una notificación específica
        
        Args:
            notification_id: ID de la notificación
            user_id: ID del usuario (para verificar permisos)
            
        Returns:
            Notification o None si no existe
        """
        try:
            notification = Notification.objects.get(id=notification_id, user_id=user_id)
            return notification
        except DoesNotExist:
            return None
        except Exception as e:
            raise NotificationServiceError(f"Error al obtener notificación: {str(e)}")
    
    def mark_notification_as_read(self, notification_id: str, user_id: str) -> bool:
        """
        Marcar una notificación como leída
        
        Args:
            notification_id: ID de la notificación
            user_id: ID del usuario (para verificar permisos)
            
        Returns:
            bool: True si se marcó como leída, False si no se encontró
        """
        try:
            notification = Notification.objects.get(id=notification_id, user_id=user_id)
            notification.mark_as_read()
            return True
        except DoesNotExist:
            return False
        except Exception as e:
            raise NotificationServiceError(f"Error al marcar notificación como leída: {str(e)}")
    
    def mark_all_notifications_as_read(self, user_id: str) -> int:
        """
        Marcar todas las notificaciones de un usuario como leídas
        
        Args:
            user_id: ID del usuario
            
        Returns:
            int: Número de notificaciones marcadas como leídas
        """
        try:
            result = Notification.objects(user_id=user_id, is_read=False).update(
                set__is_read=True,
                set__read_at=datetime.utcnow()
            )
            return result
        except Exception as e:
            raise NotificationServiceError(f"Error al marcar todas las notificaciones como leídas: {str(e)}")
    
    def get_unread_count(self, user_id: str) -> int:
        """
        Obtener el número de notificaciones no leídas de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            int: Número de notificaciones no leídas
        """
        try:
            return Notification.objects(user_id=user_id, is_read=False).count()
        except Exception as e:
            raise NotificationServiceError(f"Error al obtener conteo de notificaciones no leídas: {str(e)}")
    
    def delete_old_notifications(self, days_old: int = 30) -> int:
        """
        Eliminar notificaciones antiguas
        
        Args:
            days_old: Número de días para considerar una notificación como antigua
            
        Returns:
            int: Número de notificaciones eliminadas
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            result = Notification.objects(created_at__lt=cutoff_date).delete()
            return result
        except Exception as e:
            raise NotificationServiceError(f"Error al eliminar notificaciones antiguas: {str(e)}")
    
    def _get_report_owner(self, report_id: str) -> str:
        """
        Obtener el ID del dueño de un reporte
        
        Args:
            report_id: ID del reporte
            
        Returns:
            str: ID del usuario dueño del reporte
        """
        try:
            # Llamar al servicio de reportes para obtener información del reporte
            response = requests.get(f"{self.reports_service_url}/reports/{report_id}")
            
            if response.status_code == 200:
                report_data = response.json()
                return report_data.get('user_id')
            else:
                raise NotificationServiceError(f"No se pudo obtener información del reporte {report_id}")
                
        except requests.RequestException as e:
            raise NotificationServiceError(f"Error al conectar con el servicio de reportes: {str(e)}")
        except Exception as e:
            raise NotificationServiceError(f"Error al obtener dueño del reporte: {str(e)}")

# Instancia global del servicio
notification_service = NotificationService()
