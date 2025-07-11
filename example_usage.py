"""
Script de ejemplo para probar el servicio de notificaciones
"""
import requests
import json
import time

# Configuración
NOTIFICATIONS_API_URL = "http://localhost:5060"
REPORTS_API_URL = "http://localhost:5050"
JWT_TOKEN = "your-jwt-token-here"

# Headers para las requests
headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

def create_test_notification():
    """Crear una notificación de prueba usando el webhook"""
    print("🔔 Creando notificación de prueba...")
    
    webhook_data = {
        "report_id": "64f7b1c2d4e5f6a7b8c9d0e1",
        "response_id": "64f7b1c2d4e5f6a7b8c9d0e2",
        "response_data": {
            "type": "avistamiento",
            "comment": "Vi a la mascota en el parque cerca de la fuente principal. Se veía bien cuidada.",
            "location": [-74.0721, 4.7110],
            "images": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg"
            ],
            "created_at": "2023-09-15T10:30:00Z"
        }
    }
    
    try:
        response = requests.post(
            f"{NOTIFICATIONS_API_URL}/notifications/webhook",
            json=webhook_data,
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ Notificación creada exitosamente")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error al crear notificación: {response.status_code}")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")

def get_user_notifications():
    """Obtener notificaciones del usuario"""
    print("\n📋 Obteniendo notificaciones del usuario...")
    
    try:
        response = requests.get(
            f"{NOTIFICATIONS_API_URL}/notifications/",
            headers=headers,
            params={
                "page": 1,
                "per_page": 10,
                "unread_only": False
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Se encontraron {len(data['data']['notifications'])} notificaciones")
            
            for notification in data['data']['notifications']:
                status = "🔴 No leída" if not notification['is_read'] else "✅ Leída"
                print(f"  - {notification['title']} - {status}")
                print(f"    ID: {notification['id']}")
                print(f"    Mensaje: {notification['message']}")
                print(f"    Tipo: {notification['notification_type']}")
                print(f"    Creada: {notification['created_at']}")
                print()
                
        else:
            print(f"❌ Error al obtener notificaciones: {response.status_code}")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")

def get_notification_details(notification_id):
    """Obtener detalles de una notificación específica"""
    print(f"\n🔍 Obteniendo detalles de la notificación {notification_id}...")
    
    try:
        response = requests.get(
            f"{NOTIFICATIONS_API_URL}/notifications/{notification_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            notification = data['data']
            
            print("✅ Detalles de la notificación:")
            print(f"  Título: {notification['title']}")
            print(f"  Mensaje: {notification['message']}")
            print(f"  Tipo: {notification['notification_type']}")
            print(f"  Estado: {'Leída' if notification['is_read'] else 'No leída'}")
            print(f"  Creada: {notification['created_at']}")
            
            if notification['sighting_data']:
                print("  Datos del avistamiento:")
                sighting = notification['sighting_data']
                print(f"    Descripción: {sighting['description']}")
                print(f"    Ubicación: {sighting['location']}")
                print(f"    Imágenes: {len(sighting['images'])} imagen(es)")
                print(f"    Hora del avistamiento: {sighting['sighting_time']}")
                
        else:
            print(f"❌ Error al obtener detalles: {response.status_code}")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")

def mark_notification_as_read(notification_id):
    """Marcar una notificación como leída"""
    print(f"\n✅ Marcando notificación {notification_id} como leída...")
    
    try:
        response = requests.patch(
            f"{NOTIFICATIONS_API_URL}/notifications/{notification_id}/read",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Notificación marcada como leída")
        else:
            print(f"❌ Error al marcar como leída: {response.status_code}")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")

def get_unread_count():
    """Obtener el número de notificaciones no leídas"""
    print("\n🔢 Obteniendo conteo de notificaciones no leídas...")
    
    try:
        response = requests.get(
            f"{NOTIFICATIONS_API_URL}/notifications/unread-count",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            count = data['data']['unread_count']
            print(f"✅ Tienes {count} notificaciones no leídas")
        else:
            print(f"❌ Error al obtener conteo: {response.status_code}")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")

def mark_all_as_read():
    """Marcar todas las notificaciones como leídas"""
    print("\n✅ Marcando todas las notificaciones como leídas...")
    
    try:
        response = requests.patch(
            f"{NOTIFICATIONS_API_URL}/notifications/read-all",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Error al marcar todas como leídas: {response.status_code}")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")

def main():
    """Función principal para ejecutar el ejemplo"""
    print("🐾 PatitasBog - Ejemplo de uso del servicio de notificaciones")
    print("=" * 60)
    
    # Verificar que el JWT token está configurado
    if JWT_TOKEN == "your-jwt-token-here":
        print("⚠️  ADVERTENCIA: Configure el JWT_TOKEN en el script antes de ejecutar")
        print("   Puede obtener un token válido desde el servicio de autenticación")
        return
    
    # Flujo de ejemplo
    print("\n1. Creando notificación de prueba...")
    create_test_notification()
    
    print("\n2. Esperando un momento...")
    time.sleep(2)
    
    print("\n3. Obteniendo notificaciones del usuario...")
    get_user_notifications()
    
    print("\n4. Obteniendo conteo de notificaciones no leídas...")
    get_unread_count()
    
    # Simular obtener detalles de una notificación específica
    # (En un caso real, usaría el ID de una notificación existente)
    notification_id = "64f7b1c2d4e5f6a7b8c9d0e3"
    print(f"\n5. Obteniendo detalles de notificación {notification_id}...")
    get_notification_details(notification_id)
    
    print(f"\n6. Marcando notificación {notification_id} como leída...")
    mark_notification_as_read(notification_id)
    
    print("\n7. Obteniendo conteo actualizado...")
    get_unread_count()
    
    print("\n8. Marcando todas las notificaciones como leídas...")
    mark_all_as_read()
    
    print("\n✅ Ejemplo completado!")

if __name__ == "__main__":
    main()
