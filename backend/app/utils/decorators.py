from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app. models.user import User
from app import db

def role_required(*roles):
    """Decorador para requerir roles específicos"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = db.session.get(User, user_id)
            
            if not user:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            if user.role not in roles:
                return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator