from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.room import Room, RoomType
from app.models.user import User
from app. utils.decorators import role_required
from datetime import datetime

bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')

# ==================== ROOM TYPES ====================

@bp.route('/types', methods=['GET'])
def get_room_types():
    """Obtener todos los tipos de habitación (público)"""
    activos_only = request.args.get('activos', 'true').lower() == 'true'
    
    query = RoomType.query
    if activos_only:
        query = query.filter_by(activo=True)
    
    room_types = query.all()
    return jsonify([rt.to_dict() for rt in room_types]), 200


@bp.route('/types/<int:type_id>', methods=['GET'])
def get_room_type(type_id):
    """Obtener un tipo de habitación por ID"""
    room_type = db.session.get(RoomType, type_id)
    
    if not room_type:
        return jsonify({'error': 'Tipo de habitación no encontrado'}), 404
    
    return jsonify(room_type.to_dict()), 200


@bp.route('/types', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_room_type():
    """Crear nuevo tipo de habitación (solo admin)"""
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['nombre', 'capacidad_personas', 'precio_base']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    # Verificar que no exista un tipo con ese nombre
    existing_type = RoomType.query.filter_by(nombre=data['nombre']). first()
    if existing_type:
        return jsonify({'error': 'Ya existe un tipo de habitación con ese nombre'}), 400
    
    room_type = RoomType(
        nombre=data['nombre'],
        descripcion=data.get('descripcion'),
        capacidad_personas=data['capacidad_personas'],
        precio_base=data['precio_base'],
        amenidades=data.get('amenidades', []),
        imagenes=data.get('imagenes', []),
        activo=data.get('activo', True)
    )
    
    try:
        db.session.add(room_type)
        db.session.commit()
        return jsonify({
            'message': 'Tipo de habitación creado exitosamente',
            'room_type': room_type.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/types/<int:type_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_room_type(type_id):
    """Actualizar tipo de habitación (solo admin)"""
    room_type = db.session.get(RoomType, type_id)
    
    if not room_type:
        return jsonify({'error': 'Tipo de habitación no encontrado'}), 404
    
    data = request.get_json()
    
    # Campos actualizables
    if 'nombre' in data:
        room_type.nombre = data['nombre']
    if 'descripcion' in data:
        room_type.descripcion = data['descripcion']
    if 'capacidad_personas' in data:
        room_type.capacidad_personas = data['capacidad_personas']
    if 'precio_base' in data:
        room_type.precio_base = data['precio_base']
    if 'amenidades' in data:
        room_type.amenidades = data['amenidades']
    if 'imagenes' in data:
        room_type.imagenes = data['imagenes']
    if 'activo' in data:
        room_type. activo = data['activo']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Tipo de habitación actualizado exitosamente',
            'room_type': room_type.to_dict()
        }), 200
    except Exception as e:
        db.session. rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/types/<int:type_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_room_type(type_id):
    """Desactivar tipo de habitación (solo admin)"""
    room_type = db.session.get(RoomType, type_id)
    
    if not room_type:
        return jsonify({'error': 'Tipo de habitación no encontrado'}), 404
    
    # No eliminar, solo desactivar
    room_type.activo = False
    db.session.commit()
    
    return jsonify({'message': 'Tipo de habitación desactivado exitosamente'}), 200


# ==================== ROOMS ====================

@bp.route('/', methods=['GET'])
def get_rooms():
    """Obtener todas las habitaciones"""
    estado = request.args.get('estado')
    room_type_id = request.args.get('tipo')
    activos_only = request.args. get('activos', 'true').lower() == 'true'
    
    query = Room. query
    
    if estado:
        query = query.filter_by(estado=estado)
    if room_type_id:
        query = query.filter_by(room_type_id=room_type_id)
    if activos_only:
        query = query.filter_by(activo=True)
    
    rooms = query.all()
    return jsonify([room.to_dict() for room in rooms]), 200


@bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """Obtener una habitación por ID"""
    room = db. session.get(Room, room_id)
    
    if not room:
        return jsonify({'error': 'Habitación no encontrada'}), 404
    
    return jsonify(room. to_dict()), 200


@bp.route('/', methods=['POST'])
@jwt_required()
@role_required('admin', 'trabajador')
def create_room():
    """Crear nueva habitación (admin/trabajador)"""
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['room_type_id', 'numero_habitacion']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    # Verificar que el tipo de habitación existe
    room_type = db.session.get(RoomType, data['room_type_id'])
    if not room_type:
        return jsonify({'error': 'Tipo de habitación no encontrado'}), 404
    
    # Verificar que el número de habitación no existe
    existing_room = Room. query.filter_by(numero_habitacion=data['numero_habitacion']).first()
    if existing_room:
        return jsonify({'error': 'El número de habitación ya existe'}), 400
    
    room = Room(
        room_type_id=data['room_type_id'],
        numero_habitacion=data['numero_habitacion'],
        piso=data.get('piso'),
        estado=data.get('estado', 'disponible'),
        activo=data.get('activo', True)
    )
    
    try:
        db.session.add(room)
        db.session.commit()
        return jsonify({
            'message': 'Habitación creada exitosamente',
            'room': room.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:room_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'trabajador')
def update_room(room_id):
    """Actualizar habitación (admin/trabajador)"""
    room = db.session. get(Room, room_id)
    
    if not room:
        return jsonify({'error': 'Habitación no encontrada'}), 404
    
    data = request.get_json()
    
    # Campos actualizables
    if 'numero_habitacion' in data:
        # Verificar que no exista otro con ese número
        existing = Room.query.filter(
            Room.numero_habitacion == data['numero_habitacion'],
            Room.id != room_id
        ).first()
        if existing:
            return jsonify({'error': 'El número de habitación ya existe'}), 400
        room.numero_habitacion = data['numero_habitacion']
    
    if 'piso' in data:
        room.piso = data['piso']
    if 'estado' in data:
        room.estado = data['estado']
    if 'activo' in data:
        room.activo = data['activo']
    if 'room_type_id' in data:
        room_type = db.session.get(RoomType, data['room_type_id'])
        if not room_type:
            return jsonify({'error': 'Tipo de habitación no encontrado'}), 404
        room.room_type_id = data['room_type_id']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Habitación actualizada exitosamente',
            'room': room. to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:room_id>/estado', methods=['PATCH'])
@jwt_required()
@role_required('admin', 'trabajador')
def change_room_status(room_id):
    """Cambiar estado de habitación (admin/trabajador)"""
    room = db.session.get(Room, room_id)
    
    if not room:
        return jsonify({'error': 'Habitación no encontrada'}), 404
    
    data = request.get_json()
    
    if 'estado' not in data:
        return jsonify({'error': 'El campo estado es requerido'}), 400
    
    valid_estados = ['disponible', 'ocupada', 'limpieza', 'mantenimiento']
    if data['estado'] not in valid_estados:
        return jsonify({'error': f'Estado inválido.  Debe ser uno de: {", ".join(valid_estados)}'}), 400
    
    room.estado = data['estado']
    db.session.commit()
    
    return jsonify({
        'message': f'Estado cambiado a {data["estado"]}',
        'room': room.to_dict()
    }), 200


@bp.route('/<int:room_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_room(room_id):
    """Desactivar habitación (solo admin)"""
    room = db.session.get(Room, room_id)
    
    if not room:
        return jsonify({'error': 'Habitación no encontrada'}), 404
    
    # No eliminar, solo desactivar
    room. activo = False
    db. session.commit()
    
    return jsonify({'message': 'Habitación desactivada exitosamente'}), 200