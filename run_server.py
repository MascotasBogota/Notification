#!/usr/bin/env python3
"""
Script para iniciar el servicio de notificaciones
"""
import os
import sys
import subprocess

def main():
    """Iniciar el servicio de notificaciones"""
    print("🚀 Iniciando servicio de notificaciones...")
    
    # Asegurarse de que estamos en el directorio correcto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"📁 Directorio actual: {os.getcwd()}")
    
    # Verificar que app.py existe
    if not os.path.exists('app.py'):
        print("❌ Error: app.py no encontrado")
        sys.exit(1)
    
    # Ejecutar la aplicación
    try:
        import app
        app.create_app().run(host="0.0.0.0", port=5010, debug=True)
    except Exception as e:
        print(f"❌ Error ejecutando la aplicación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
