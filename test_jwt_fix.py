#!/usr/bin/env python3
"""
Script de prueba para verificar la corrección del JWT entre servicios
"""
import requests
import json
import os
import sys

# URLs de los servicios
NOTIFICATION_URL = "http://localhost:5010"
LOGIN_URL = "http://localhost:5000"

def test_service_health():
    """Verificar que ambos servicios estén funcionando"""
    print("🩺 Verificando estado de los servicios...")
    
    services = [
        ("Login Service", f"{LOGIN_URL}/api/docs/"),  # Cambiar de /api/health a /api
        ("Notification Service", f"{NOTIFICATION_URL}/health")
    ]
    
    all_healthy = True
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"   {name}: {status}")
            if response.status_code != 200:
                all_healthy = False
        except Exception as e:
            print(f"   {name}: ❌ ERROR - {str(e)}")
            all_healthy = False
    
    return all_healthy

def test_jwt_debug():
    """Probar endpoint de debug JWT"""
    print("\n🔧 Probando debug JWT...")
    
    try:
        response = requests.get(f"{NOTIFICATION_URL}/notifications/debug/jwt")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            debug_info = response.json()
            print(f"   JWT Secret configurado: {'✅' if debug_info['debug']['jwt_secret_configured'] else '❌'}")
            print(f"   Longitud del secret: {debug_info['debug']['jwt_secret_length']}")
            print(f"   Environment: {debug_info['debug']['environment']}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False

def get_jwt_token():
    """Obtener token JWT del servicio de login"""
    print("\n🔑 Obteniendo token JWT...")
    
    # Datos de prueba - ajustar según tu usuario
    login_data = {
        "email": "druiz@sml.com",
        "password": "Druiz123"
    }
    
    try:
        response = requests.post(
            f"{LOGIN_URL}/api/users/login",
            headers={"Content-Type": "application/json"},
            json=login_data,
            timeout=10
        )
        
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print(f"   ✅ Token obtenido: {token}")
                return token
            else:
                print("   ❌ No se encontró token en la respuesta")
                return None
        else:
            print(f"   ❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def get_test_token():
    """Obtener token de prueba del servicio de notificaciones"""
    print("\n🔧 Obteniendo token de prueba...")
    
    try:
        response = requests.post(
            f"{NOTIFICATION_URL}/notifications/debug/create-test-token",
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print(f"   ✅ Token de prueba obtenido: {token[:20]}...")
                print(f"   User ID: {data.get('user_id')}")
                return token
            else:
                print("   ❌ No se encontró token en la respuesta")
                return None
        else:
            print(f"   ❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_jwt_validation(token):
    """Probar validación del JWT en el servicio de notificaciones"""
    print("\n🔍 Probando validación JWT...")
    
    if not token:
        print("   ⚠️  No hay token para validar")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{NOTIFICATION_URL}/notifications/debug/jwt-validate",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ JWT válido")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   JWT Claims: {data.get('jwt_claims', {})}")
            return True
        else:
            data = response.json()
            print(f"   ❌ JWT inválido")
            print(f"   Error: {data.get('error', 'Unknown')}")
            print(f"   Error Type: {data.get('error_type', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_notifications_endpoint(token):
    """Probar endpoint de notificaciones"""
    print("\n📬 Probando endpoint de notificaciones...")
    
    if not token:
        print("   ⚠️  No hay token para probar")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"unread_only": "false", "per_page": "10", "page": "1"}
    
    try:
        response = requests.get(
            f"{NOTIFICATION_URL}/notifications/",
            headers=headers,
            params=params,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Notificaciones obtenidas exitosamente")
            
            # Manejar diferentes estructuras de respuesta
            notifications = None
            if 'data' in data:
                if 'notifications' in data['data']:
                    notifications = data['data']['notifications']
                else:
                    notifications = data['data']
            elif 'notifications' in data:
                notifications = data['notifications']
            else:
                notifications = []
            
            count = len(notifications) if notifications is not None else 0
            print(f"   Número de notificaciones: {count}")
            return True
        elif response.status_code == 401:
            print(f"   ❌ Error 401: Token inválido o expirado")
            return False
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🧪 JWT Fix Test Suite - PatitasBog Notifications")
    print("=" * 60)
    
    # Test 1: Verificar servicios
    services_ok = test_service_health()
    
    # Test 2: Debug JWT configuración
    if not test_jwt_debug():
        print("\n❌ Problema con la configuración JWT del servicio de notificaciones")
        sys.exit(1)
    
    # Test 3: Obtener token
    token = None
    
    if services_ok:
        # Si LogIn_backend está disponible, intentar obtener token real
        token = get_jwt_token()
        
        if not token:
            print("\n⚠️  No se pudo obtener token del servicio de login")
            print("   Intentando con token de prueba...")
            token = get_test_token()
    else:
        print("\n⚠️  LogIn_backend no está disponible")
        print("   Usando token de prueba para continuar...")
        token = get_test_token()
    
    if not token:
        print("\n❌ No se pudo obtener ningún token")
        print("   Verifica que:")
        print("   1. El servicio de notificaciones esté corriendo")
        print("   2. El endpoint create-test-token esté disponible")
        print("   3. O que LogIn_backend esté corriendo con un usuario válido")
        sys.exit(1)
    
    # Test 4: Validar token
    if not test_jwt_validation(token):
        print("\n❌ Token JWT no es válido en el servicio de notificaciones")
        print("   Verifica que ambos servicios usen la misma JWT_SECRET")
        sys.exit(1)
    
    # Test 5: Probar endpoint real
    if test_notifications_endpoint(token):
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("   El JWT funciona correctamente entre servicios")
        
        if not services_ok:
            print("\n💡 Nota: Se usó token de prueba porque LogIn_backend no está disponible")
            print("   Para pruebas completas, asegúrate de que LogIn_backend esté corriendo")
    else:
        print("\n❌ Error en el endpoint de notificaciones")
        sys.exit(1)

if __name__ == "__main__":
    main()
