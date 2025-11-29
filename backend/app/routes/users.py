from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.utils.decorators import role_required
import secrets
import string

bp = Blueprint('users', __name__, url_prefix='/api/users')

def generate_random_password(length=10):
    """Generar contraseña aleatoria"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets. choice(characters) for _ in range(length))

def generate_email_from_name(nombre_completo):
    """Generar email corporativo desde el nombre"""
    nombres = nombre_completo.lower().split()
    if len(nombres) >= 2:
        email = f"{nombres[0]}.{nombres[-1]}@metricshotel.com"
    else:
        email = f"{nombres[0]}@metricshotel.com"
    
    # Si el email ya existe, agregar número
    counter = 1
    original_email = email
    while User.query.filter_by(email=email).first():
        email = original_email. replace('@', f'{counter}@')
        counter += 1
    
    return email

@bp.route('/', methods=['GET'])
@jwt_required()
@role_required('admin', 'trabajador')
def get_users():
    """Obtener lista de usuarios (admin/trabajador)"""
    role_filter = request.args.get('role')
    activos_only = request.args.get('activos', 'true').lower() == 'true'
    
    query = User.query
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    if activos_only:
        query = query.filter_by(activo=True)
    
    users = query.all()
    return jsonify([user.to_dict() for user in users]), 200


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required('admin', 'trabajador')
def get_user(user_id):
    """Obtener un usuario por ID (admin/trabajador)"""
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify(user.to_dict()), 200


@bp.route('/create-worker', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_worker():
    """Crear trabajador o admin (solo admin)"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['nombre_completo', 'rut', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    # Validar rol
    if data['role'] not in ['trabajador', 'admin']:
        return jsonify({'error': 'El rol debe ser trabajador o admin'}), 400
    
    # Verificar si el RUT ya existe
    if User. query.filter_by(rut=data['rut']).first():
        return jsonify({'error': 'El RUT ya está registrado'}), 400
    
    # Generar email corporativo
    email = generate_email_from_name(data['nombre_completo'])
    
    # Generar contraseña temporal
    temp_password = generate_random_password()
    
    # Crear usuario
    user = User(
        email=email,
        nombre_completo=data['nombre_completo'],
        rut=data['rut'],
        edad=data.get('edad'),
        telefono=data.get('telefono'),
        direccion=data. get('direccion'),
        role=data['role'],
        creado_por_id=current_user_id,
        debe_cambiar_password=True
    )
    user.set_password(temp_password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Trabajador creado exitosamente',
            'user': user.to_dict(),
            'credentials': {
                'email': email,
                'password': temp_password,
                'note': 'Debe cambiar la contraseña en el primer login'
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user(user_id):
    """Actualizar usuario (solo admin)"""
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Campos actualizables
    if 'nombre_completo' in data:
        user.nombre_completo = data['nombre_completo']
    if 'edad' in data:
        user. edad = data['edad']
    if 'telefono' in data:
        user.telefono = data['telefono']
    if 'direccion' in data:
        user.direccion = data['direccion']
    if 'activo' in data:
        user.activo = data['activo']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Usuario actualizado exitosamente',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def deactivate_user(user_id):
    """Desactivar usuario (solo admin)"""
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    if user.role == 'admin':
        return jsonify({'error': 'No se puede desactivar un administrador'}), 403
    
    user.activo = False
    db.session.commit()
    
    return jsonify({'message': 'Usuario desactivado exitosamente'}), 200