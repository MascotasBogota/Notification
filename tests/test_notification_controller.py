import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from src.controllers.notification_controller import NotificationController
from src.services.notification_service import NotificationServiceError

class TestNotificationController:
    """Tests para el controlador de notificaciones"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock del usuario actual
        self.mock_user = {'user_id': 'user123'}
    
    @patch('src.controllers.notification_controller.get_current_user')
    @patch('src.controllers.notification_controller.notification_service')
    def test_get_user_notifications_success(self, mock_service, mock_get_user):
        """Test obtener notificaciones de usuario exitosamente"""
        # Configurar mocks
        mock_get_user.return_value = self.mock_user
        mock_service.get_user_notifications.return_value = {
            'notifications': [{'id': 'notif123'}],
            'pagination': {'page': 1, 'total': 1}
        }
        
        with self.app.test_request_context('/?page=1&per_page=10'):
            with patch('src.controllers.notification_controller.jwt_required', lambda f: f):
                # Ejecutar
                response = NotificationController.get_user_notifications()
                
                # Verificar
                assert response[1] == 200
                data = response[0].get_json()
                assert data['success'] is True
                assert 'notifications' in data['data']
    
    @patch('src.controllers.notification_controller.get_current_user')
    @patch('src.controllers.notification_controller.notification_service')
    def test_get_user_notifications_invalid_page(self, mock_service, mock_get_user):
        """Test obtener notificaciones con página inválida"""
        # Configurar mocks
        mock_get_user.return_value = self.mock_user
        
        with self.app.test_request_context('/?page=0'):
            with patch('src.controllers.notification_controller.jwt_required', lambda f: f):
                # Ejecutar
                response = NotificationController.get_user_notifications()
                
                # Verificar
                assert response[1] == 400
                data = response[0].get_json()
                assert 'error' in data
    
    @patch('src.controllers.notification_controller.get_current_user')
    @patch('src.controllers.notification_controller.notification_service')
    def test_get_notification_by_id_success(self, mock_service, mock_get_user):
        """Test obtener notificación por ID exitosamente"""
        # Configurar mocks
        mock_get_user.return_value = self.mock_user
        mock_notification = MagicMock()
        mock_notification.to_dict.return_value = {'id': 'notif123'}
        mock_service.get_notification_by_id.return_value = mock_notification
        
        with self.app.test_request_context():
            with patch('src.controllers.notification_controller.jwt_required', lambda f: f):
                # Ejecutar
                response = NotificationController.get_notification_by_id('notif123')
                
                # Verificar
                assert response[1] == 200
                data = response[0].get_json()
                assert data['success'] is True
                assert data['data']['id'] == 'notif123'
    
    @patch('src.controllers.notification_controller.get_current_user')
    @patch('src.controllers.notification_controller.notification_service')
    def test_get_notification_by_id_not_found(self, mock_service, mock_get_user):
        """Test obtener notificación por ID cuando no existe"""
        # Configurar mocks
        mock_get_user.return_value = self.mock_user
        mock_service.get_notification_by_id.return_value = None
        
        with self.app.test_request_context():
            with patch('src.controllers.notification_controller.jwt_required', lambda f: f):
                # Ejecutar
                response = NotificationController.get_notification_by_id('invalid_id')
                
                # Verificar
                assert response[1] == 404
                data = response[0].get_json()
                assert 'error' in data
    
    @patch('src.controllers.notification_controller.get_current_user')
    @patch('src.controllers.notification_controller.notification_service')
    def test_mark_notification_as_read_success(self, mock_service, mock_get_user):
        """Test marcar notificación como leída exitosamente"""
        # Configurar mocks
        mock_get_user.return_value = self.mock_user
        mock_service.mark_notification_as_read.return_value = True
        
        with self.app.test_request_context():
            with patch('src.controllers.notification_controller.jwt_required', lambda f: f):
                # Ejecutar
                response = NotificationController.mark_notification_as_read('notif123')
                
                # Verificar
                assert response[1] == 200
                data = response[0].get_json()
                assert data['success'] is True
    
    @patch('src.controllers.notification_controller.notification_service')
    def test_create_notification_success(self, mock_service):
        """Test crear notificación exitosamente"""
        # Configurar mocks
        mock_notification = MagicMock()
        mock_notification.to_dict.return_value = {'id': 'notif123'}
        mock_service.create_notification.return_value = mock_notification
        
        mock_data = {
            'report_id': 'report123',
            'response_id': 'response123',
            'response_data': {
                'type': 'avistamiento',
                'comment': 'Test comment'
            }
        }
        
        with self.app.test_request_context(json=mock_data):
            # Ejecutar
            response = NotificationController.create_notification()
            
            # Verificar
            assert response[1] == 201
            data = response[0].get_json()
            assert data['success'] is True
            assert data['data']['id'] == 'notif123'
    
    def test_create_notification_missing_data(self):
        """Test crear notificación con datos faltantes"""
        with self.app.test_request_context(json={}):
            # Ejecutar
            response = NotificationController.create_notification()
            
            # Verificar
            assert response[1] == 400
            data = response[0].get_json()
            assert 'error' in data
