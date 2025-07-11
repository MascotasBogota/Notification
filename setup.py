#!/usr/bin/env python3
"""
Script de instalación y configuración para el servicio de notificaciones
"""
import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, description):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Completado")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error:")
        print(f"   Comando: {command}")
        print(f"   Código de salida: {e.returncode}")
        print(f"   Error: {e.stderr}")
        return None

def check_python_version():
    """Verificar la versión de Python"""
    print("🐍 Verificando versión de Python...")
    if sys.version_info < (3, 9):
        print("❌ Se requiere Python 3.9 o superior")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

def check_dependencies():
    """Verificar dependencias del sistema"""
    print("📦 Verificando dependencias del sistema...")
    
    dependencies = {
        'git': 'git --version',
        'docker': 'docker --version',
        'docker-compose': 'docker-compose --version'
    }
    
    for dep, command in dependencies.items():
        if shutil.which(dep.split()[0]):
            print(f"✅ {dep} está instalado")
        else:
            print(f"⚠️  {dep} no está instalado (opcional)")

def create_virtual_environment():
    """Crear entorno virtual"""
    venv_path = Path('venv')
    if venv_path.exists():
        print("✅ Entorno virtual ya existe")
        return
    
    return run_command(f"{sys.executable} -m venv venv", "Creando entorno virtual")

def install_requirements():
    """Instalar dependencias de Python"""
    if os.name == 'nt':  # Windows
        pip_command = r"venv\Scripts\pip.exe install -r requirements.txt"
    else:  # Linux/Mac
        pip_command = "venv/bin/pip install -r requirements.txt"
    
    return run_command(pip_command, "Instalando dependencias de Python")

def setup_environment_file():
    """Configurar archivo de variables de entorno"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Archivo .env creado desde .env.example")
        print("⚠️  Por favor, edite el archivo .env con sus configuraciones")
    else:
        print("⚠️  Archivo .env.example no encontrado")

def run_tests():
    """Ejecutar tests del proyecto"""
    if os.name == 'nt':  # Windows
        pytest_command = r"venv\Scripts\pytest.exe tests/ -v"
    else:  # Linux/Mac
        pytest_command = "venv/bin/pytest tests/ -v"
    
    return run_command(pytest_command, "Ejecutando tests")

def start_service():
    """Iniciar el servicio"""
    print("🚀 Iniciando servicio de notificaciones...")
    
    if os.name == 'nt':  # Windows
        python_command = r"venv\Scripts\python.exe app.py"
    else:  # Linux/Mac
        python_command = "venv/bin/python app.py"
    
    print(f"   Comando: {python_command}")
    print("   Para iniciar el servicio ejecute:")
    print(f"   {python_command}")
    print("   O use Docker: docker-compose up --build")

def main():
    """Función principal"""
    print("🐾 PatitasBog - Instalación del Servicio de Notificaciones")
    print("=" * 60)
    
    # Verificar prerrequisitos
    check_python_version()
    check_dependencies()
    
    # Configurar entorno de desarrollo
    create_virtual_environment()
    install_requirements()
    setup_environment_file()
    
    # Ejecutar tests
    print("\n🧪 Ejecutando tests...")
    run_tests()
    
    # Información final
    print("\n" + "=" * 60)
    print("✅ Instalación completada!")
    print("\n📝 Próximos pasos:")
    print("1. Edite el archivo .env con sus configuraciones")
    print("2. Configure la conexión a MongoDB Atlas")
    print("3. Configure las URLs de otros servicios")
    print("4. Inicie el servicio con uno de estos comandos:")
    print("   - Desarrollo: python app.py")
    print("   - Docker: docker-compose up --build")
    print("   - Producción: gunicorn --bind 0.0.0.0:5060 app:create_app()")
    print("\n🌐 URLs útiles:")
    print("   - API: http://localhost:5060")
    print("   - Documentación: http://localhost:5060/docs/")
    print("   - Health check: http://localhost:5060/health")

if __name__ == "__main__":
    main()
