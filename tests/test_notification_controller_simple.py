import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, request
from src.controllers.notification_controller import NotificationController

class TestNotificationControllerSimple:
    """Tests simplificados para el controlador de notificaciones"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        
        self.mock_user = {
            'user_id': 'test_user_123',
            'email': 'test@example.com'
        }
    
    def test_create_notification_success(self):
        """Test crear notificación exitosamente (webhook)"""
        test_data = {
            'report_id': 'report123',
            'response_id': 'response456',
            'response_data': {
                'type': 'avistamiento',
                'comment': 'Vi a la mascota en el parque',
                'location': [-74.0721, 4.7110],
                'images': ['http://example.com/image1.jpg'],
                'created_at': '2023-09-15T10:30:00Z'
            }
        }
        
        with self.app.test_request_context(
            '/notifications/webhook',
            method='POST',
            json=test_data
        ):
            with patch('src.controllers.notification_controller.notification_service') as mock_service:
                mock_notification = MagicMock()
                mock_notification.to_dict.return_value = {'id': 'notif123'}
                mock_service.create_notification.return_value = mock_notification
                
                response = NotificationController.create_notification()
                
                assert response[1] == 201
                assert 'success' in response[0].data.decode()
    
    def test_create_notification_missing_data(self):
        """Test crear notificación con datos faltantes"""
        with self.app.test_request_context(
            '/notifications/webhook',
            method='POST',
            json={}
        ):
            response = NotificationController.create_notification()
            
            assert response[1] == 400
            assert 'error' in response[0].data.decode()
    
    @patch('src.controllers.notification_controller.get_current_user')
    @patch('src.controllers.notification_controller.verify_jwt_in_request')
    def test_get_unread_count_success(self, mock_verify_jwt, mock_get_user):
        """Test obtener conteo de notificaciones no leídas"""
        # Configurar mocks
        mock_verify_jwt.return_value = None  # JWT válido
        mock_get_user.return_value = self.mock_user
        
        with self.app.test_request_context():
            with patch('src.controllers.notification_controller.notification_service') as mock_service:
                mock_service.get_unread_count.return_value = 5
                
                response = NotificationController.get_unread_count()
                
                assert response[1] == 200
                response_data = response[0].get_json()
                assert response_data['success'] is True
                assert response_data['data']['unread_count'] == 5
