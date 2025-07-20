from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
import os

def jwt_required(f):
    """
    Decorador para proteger rutas con JWT usando Flask-JWT-Extended
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token inválido o expirado', 'message': str(e)}), 401
    
    return decorated_function

def get_current_user():
    """
    Obtener el usuario actual desde el token JWT
    """
    try:
        # Intentar obtener user_id con get_jwt_identity() (para tokens con 'sub')
        user_id = get_jwt_identity()
        
        # Si no hay user_id, intentar obtenerlo desde claims con 'userId' (compatibilidad)
        if not user_id:
            claims = get_jwt()
            user_id = claims.get('userId')
        
        # Si aún no hay user_id, usar 'sub' directamente de claims
        if not user_id:
            claims = get_jwt()
            user_id = claims.get('sub')
            
        return {
            'user_id': user_id,
            'claims': get_jwt()
        }
    except Exception:
        return None
