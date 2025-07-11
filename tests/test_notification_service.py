import pytest
from unittest.mock import patch, MagicMock
from src.services.notification_service import NotificationService, NotificationServiceError
from src.models.notification_model import Notification
from datetime import datetime

class TestNotificationService:
    """Tests para el servicio de notificaciones"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.service = NotificationService()
        self.mock_response_data = {
            'type': 'avistamiento',
            'comment': 'Vi a la mascota en el parque',
            'location': [-74.0721, 4.7110],
            'images': ['http://example.com/image1.jpg'],
            'created_at': datetime.utcnow()
        }
    
    @patch('src.services.notification_service.requests.get')
    @patch('src.models.notification_model.Notification.save')
    def test_create_notification_success(self, mock_save, mock_get):
        """Test crear notificación exitosamente"""
        # Configurar mock
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'user_id': 'user123'}
        
        # Ejecutar
        result = self.service.create_notification(
            report_id='report123',
            response_id='response123',
            response_data=self.mock_response_data
        )
        
        # Verificar
        assert isinstance(result, Notification)
        assert result.user_id == 'user123'
        assert result.report_id == 'report123'
        assert result.response_id == 'response123'
        assert result.notification_type == 'avistamiento'
        mock_save.assert_called_once()
    
    @patch('src.services.notification_service.requests.get')
    def test_create_notification_report_not_found(self, mock_get):
        """Test crear notificación cuando el reporte no existe"""
        # Configurar mock
        mock_get.return_value.status_code = 404
        
        # Ejecutar y verificar
        with pytest.raises(NotificationServiceError):
            self.service.create_notification(
                report_id='invalid_report',
                response_id='response123',
                response_data=self.mock_response_data
            )
    
    @patch('src.models.notification_model.Notification.objects')
    def test_get_user_notifications_success(self, mock_objects):
        """Test obtener notificaciones de usuario exitosamente"""
        # Configurar mock
        mock_notification = MagicMock()
        mock_notification.to_dict.return_value = {'id': 'notif123'}
        
        mock_objects.return_value.count.return_value = 1
        mock_objects.return_value.order_by.return_value.skip.return_value.limit.return_value = [mock_notification]
        
        # Ejecutar
        result = self.service.get_user_notifications('user123')
        
        # Verificar
        assert result['notifications'] == [{'id': 'notif123'}]
        assert result['pagination']['total'] == 1
        assert result['pagination']['page'] == 1
    
    @patch('src.models.notification_model.Notification.objects')
    def test_mark_notification_as_read_success(self, mock_objects):
        """Test marcar notificación como leída exitosamente"""
        # Configurar mock
        mock_notification = MagicMock()
        mock_objects.get.return_value = mock_notification
        
        # Ejecutar
        result = self.service.mark_notification_as_read('notif123', 'user123')
        
        # Verificar
        assert result is True
        mock_notification.mark_as_read.assert_called_once()
    
    @patch('src.models.notification_model.Notification.objects')
    def test_mark_notification_as_read_not_found(self, mock_objects):
        """Test marcar notificación como leída cuando no existe"""
        # Configurar mock
        from mongoengine import DoesNotExist
        mock_objects.get.side_effect = DoesNotExist()
        
        # Ejecutar
        result = self.service.mark_notification_as_read('invalid_notif', 'user123')
        
        # Verificar
        assert result is False
    
    @patch('src.models.notification_model.Notification.objects')
    def test_get_unread_count_success(self, mock_objects):
        """Test obtener conteo de notificaciones no leídas"""
        # Configurar mock
        mock_objects.return_value.count.return_value = 5
        
        # Ejecutar
        result = self.service.get_unread_count('user123')
        
        # Verificar
        assert result == 5
        mock_objects.assert_called_with(user_id='user123', is_read=False)
