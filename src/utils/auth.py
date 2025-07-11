from functools import wraps
from flask import request, jsonify
import jwt
import os

def jwt_required(f):
    """
    Decorador para proteger rutas con JWT
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer <token>"
            except IndexError:
                return jsonify({'error': 'Token malformado'}), 401
        
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        try:
            # Decodificar el token
            secret_key = os.getenv('JWT_SECRET_KEY', 'patitas-bog-jwt-secret')
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            request.current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """
    Obtener el usuario actual desde el token JWT
    """
    return getattr(request, 'current_user', None)
