from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField, PointField
from datetime import datetime

class Notification(Document):
    """
    Modelo de Notificación para avistamientos de mascotas perdidas
    """
    meta = {
        'collection': 'notifications',
        'indexes': [
            {'fields': ['user_id', '-created_at']},
            {'fields': ['report_id', '-created_at']},
            {'fields': ['is_read', '-created_at']},
            {'fields': ['notification_type', '-created_at']}
        ]
    }
    
    # ID del usuario que debe recibir la notificación (dueño del reporte)
    user_id = StringField(required=True)
    
    # ID del reporte al que se refiere la notificación
    report_id = StringField(required=True)
    
    # ID de la respuesta/avistamiento que generó la notificación
    response_id = StringField(required=True)
    
    # Tipo de notificación
    notification_type = StringField(required=True, choices=['avistamiento', 'hallazgo'], default='avistamiento')
    
    # Título de la notificación
    title = StringField(required=True, max_length=100)
    
    # Mensaje de la notificación
    message = StringField(required=True, max_length=500)
    
    # Datos del avistamiento (sin datos personales del usuario que reportó)
    sighting_data = {
        'description': StringField(),
        'location': PointField(),
        'images': ListField(StringField()),
        'sighting_time': DateTimeField()
    }
    
    # Estado de la notificación
    is_read = BooleanField(default=False)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    read_at = DateTimeField()
    
    def mark_as_read(self):
        """Marcar la notificación como leída"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.save()
    
    def to_dict(self):
        """Convertir a diccionario para serialización"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'report_id': self.report_id,
            'response_id': self.response_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'sighting_data': {
                'description': self.sighting_data.get('description'),
                'location': self.sighting_data.get('location'),
                'images': self.sighting_data.get('images', []),
                'sighting_time': self.sighting_data.get('sighting_time').isoformat() if self.sighting_data.get('sighting_time') else None
            },
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
