from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Registrar nuevo usuario (cliente)"""
    data = request. get_json()
    
    # Validar campos requeridos
    required_fields = ['email', 'password', 'nombre_completo', 'rut']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    # Verificar si el email ya existe
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya está registrado'}), 400
    
    # Verificar si el RUT ya existe
    if User.query.filter_by(rut=data['rut']).first():
        return jsonify({'error': 'El RUT ya está registrado'}), 400
    
    # Crear nuevo usuario
    user = User(
        email=data['email'],
        nombre_completo=data['nombre_completo'],
        rut=data['rut'],
        edad=data. get('edad'),
        telefono=data.get('telefono'),
        direccion=data.get('direccion'),
        role='cliente'
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Crear token de acceso
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db. session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Iniciar sesión"""
    data = request.get_json()
    
    # Validar campos requeridos
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400
    
    # Buscar usuario por email
    user = User.query.filter_by(email=data['email']).first()
    
    # Verificar usuario y contraseña
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Verificar si está activo
    if not user.activo:
        return jsonify({'error': 'Usuario inactivo'}), 403
    
    # Actualizar última conexión
    user.ultima_conexion = datetime.utcnow()
    db.session.commit()
    
    # Crear token de acceso
    access_token = create_access_token(identity=str(user. id))
    
    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'user': user.to_dict(),
        'debe_cambiar_password': user.debe_cambiar_password
    }), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtener información del usuario actual"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify(user.to_dict()), 200


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Cambiar contraseña del usuario actual"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar campos requeridos
    if 'current_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Contraseña actual y nueva contraseña son requeridas'}), 400
    
    # Verificar contraseña actual
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401
    
    # Establecer nueva contraseña
    user.set_password(data['new_password'])
    user.debe_cambiar_password = False
    db.session.commit()
    
    return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200