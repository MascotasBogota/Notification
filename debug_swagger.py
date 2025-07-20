#!/usr/bin/env python3
"""
Script para comparar peticiones Test vs Swagger
"""
import requests
import json

NOTIFICATION_URL = "http://localhost:5010"
LOGIN_URL = "http://localhost:5000"

def get_token():
    """Obtener token del servicio de login"""
    login_data = {
        "email": "druiz@sml.com", 
        "password": "Druiz123"
    }
    
    response = requests.post(
        f"{LOGIN_URL}/api/users/login",
        headers={"Content-Type": "application/json"},
        json=login_data
    )
    
    if response.status_code == 200:
        return response.json().get('token')
    return None

def test_headers_debug(token, test_name, headers):
    """Probar el endpoint de debug de headers"""
    print(f"\n🔍 {test_name}")
    
    # Probar debug de headers
    debug_response = requests.get(
        f"{NOTIFICATION_URL}/notifications/debug/request-headers",
        headers=headers
    )
    
    print(f"   Debug Status: {debug_response.status_code}")
    if debug_response.status_code == 200:
        debug_data = debug_response.json()
        auth_header = debug_data.get('authorization_header')
        user_agent = debug_data.get('user_agent', 'None')
        print(f"   Authorization Header: {auth_header}")
        print(f"   User-Agent: {user_agent[:50]}..." if user_agent and len(user_agent) > 50 else f"   User-Agent: {user_agent}")
    
    # Probar endpoint real
    response = requests.get(
        f"{NOTIFICATION_URL}/notifications/",
        headers=headers,
        params={"unread_only": "false", "per_page": "10", "page": "1"}
    )
    
    print(f"   Notifications Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    
    return response.status_code == 200

def test_with_different_formats(token):
    """Probar el mismo endpoint con diferentes formatos de header"""
    
    test_cases = [
        {
            "name": "Formato Python requests (como en test)",
            "headers": {"Authorization": f"Bearer {token}"}
        },
        {
            "name": "Formato Swagger UI típico",
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        },
        {
            "name": "Formato con User-Agent de navegador",
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json", 
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        },
        {
            "name": "Formato Bearer sin espacios extra",
            "headers": {"Authorization": f"Bearer{token}"}  # SIN ESPACIO
        },
        {
            "name": "Formato Bearer con espacios extra",
            "headers": {"Authorization": f"Bearer  {token}"}  # DOS ESPACIOS
        },
        {
            "name": "Formato Bearer duplicado",
            "headers": {"Authorization": f"Bearer Bearer {token}"}  # DUPLICADO
        }
    ]
    
    results = []
    for test_case in test_cases:
        success = test_headers_debug(token, test_case['name'], test_case['headers'])
        results.append((test_case['name'], success))
    
    return results

def test_exact_swagger_simulation():
    """Simular exactamente lo que hace Swagger UI"""
    print(f"\n🌐 Simulando petición exacta de Swagger UI...")
    
    token = get_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    # Headers exactos que suele enviar Swagger UI
    swagger_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    
    return test_headers_debug(token, "Simulación exacta de Swagger", swagger_headers)

def main():
    print("🧪 Comparación Test vs Swagger - Debug Headers")
    print("=" * 60)
    
    token = get_token()
    if not token:
        print("❌ No se pudo obtener token")
        return
    
    print(f"✅ Token obtenido: {token[:30]}...")
    
    # Probar diferentes formatos
    results = test_with_different_formats(token)
    
    # Probar simulación exacta de Swagger
    swagger_success = test_exact_swagger_simulation()
    
    # Resumen
    print(f"\n📊 Resumen de Resultados:")
    print("=" * 40)
    
    for name, success in results:
        status = "✅ OK" if success else "❌ FAIL"
        print(f"   {status} {name}")
    
    swagger_status = "✅ OK" if swagger_success else "❌ FAIL"
    print(f"   {swagger_status} Simulación exacta de Swagger")
    
    print(f"\n💡 Recomendaciones:")
    if any(not success for _, success in results):
        print("   - Verifica el formato exacto del token en Swagger")
        print("   - Asegúrate de no tener espacios extra")
        print("   - Verifica que no haya prefijo 'Bearer' duplicado")
    else:
        print("   - Todos los formatos funcionan correctamente")
        print("   - El problema puede estar en cómo Swagger está enviando el token")

if __name__ == "__main__":
    main()
