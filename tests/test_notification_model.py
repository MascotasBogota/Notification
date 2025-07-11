import pytest
from datetime import datetime
from src.models.notification_model import Notification

class TestNotificationModel:
    """Tests para el modelo de notificación"""
    
    def test_notification_creation(self):
        """Test crear una notificación"""
        notification = Notification(
            user_id='user123',
            report_id='report123',
            response_id='response123',
            notification_type='avistamiento',
            title='Nuevo avistamiento',
            message='Se ha registrado un nuevo avistamiento',
            sighting_data={
                'description': 'Vi a la mascota en el parque',
                'location': [-74.0721, 4.7110],
                'images': ['http://example.com/image1.jpg'],
                'sighting_time': datetime.utcnow()
            }
        )
        
        # Verificar
        assert notification.user_id == 'user123'
        assert notification.report_id == 'report123'
        assert notification.response_id == 'response123'
        assert notification.notification_type == 'avistamiento'
        assert notification.title == 'Nuevo avistamiento'
        assert notification.is_read is False
        assert notification.created_at is not None
    
    def test_notification_to_dict(self):
        """Test convertir notificación a diccionario"""
        sighting_time = datetime.utcnow()
        notification = Notification(
            user_id='user123',
            report_id='report123',
            response_id='response123',
            notification_type='avistamiento',
            title='Nuevo avistamiento',
            message='Se ha registrado un nuevo avistamiento',
            sighting_data={
                'description': 'Vi a la mascota en el parque',
                'location': [-74.0721, 4.7110],
                'images': ['http://example.com/image1.jpg'],
                'sighting_time': sighting_time
            }
        )
        
        # Ejecutar
        result = notification.to_dict()
        
        # Verificar
        assert result['user_id'] == 'user123'
        assert result['report_id'] == 'report123'
        assert result['response_id'] == 'response123'
        assert result['notification_type'] == 'avistamiento'
        assert result['title'] == 'Nuevo avistamiento'
        assert result['is_read'] is False
        assert 'sighting_data' in result
        assert result['sighting_data']['description'] == 'Vi a la mascota en el parque'
        assert result['sighting_data']['location'] == [-74.0721, 4.7110]
        assert result['sighting_data']['images'] == ['http://example.com/image1.jpg']
    
    def test_mark_as_read(self):
        """Test marcar notificación como leída"""
        notification = Notification(
            user_id='user123',
            report_id='report123',
            response_id='response123',
            notification_type='avistamiento',
            title='Nuevo avistamiento',
            message='Se ha registrado un nuevo avistamiento'
        )
        
        # Verificar estado inicial
        assert notification.is_read is False
        assert notification.read_at is None
        
        # Marcar como leída (mock save)
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        # Verificar
        assert notification.is_read is True
        assert notification.read_at is not None
