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
        user_id = get_jwt_identity()
        claims = get_jwt()
        return {
            'user_id': user_id,
            'claims': claims
        }
    except Exception:
        return None
