from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.booking import Booking
from app.models.room import Room
from app.models.user import User
from app.utils.decorators import role_required
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

def check_room_availability(room_id, check_in, check_out, exclude_booking_id=None):
    """Verificar si una habitación está disponible en las fechas dadas"""
    query = Booking.query. filter(
        Booking.room_id == room_id,
        Booking.estado. in_(['pendiente', 'confirmada', 'check_in_realizado']),
        or_(
            and_(Booking.check_in <= check_in, Booking.check_out > check_in),
            and_(Booking.check_in < check_out, Booking.check_out >= check_out),
            and_(Booking.check_in >= check_in, Booking.check_out <= check_out)
        )
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    return query.first() is None


@bp.route('/', methods=['GET'])
@jwt_required()
def get_bookings():
    """Obtener reservas (filtradas por rol)"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    
    # Filtros
    estado = request.args. get('estado')
    room_id = request.args.get('room_id')
    user_filter = request.args.get('user_id')
    
    query = Booking.query
    
    # Si es cliente, solo ver sus propias reservas
    if user.role == 'cliente':
        query = query.filter_by(user_id=user_id)
    # Si es trabajador/admin, puede filtrar por usuario
    elif user_filter:
        query = query. filter_by(user_id=user_filter)
    
    if estado:
        query = query. filter_by(estado=estado)
    if room_id:
        query = query.filter_by(room_id=room_id)
    
    bookings = query.order_by(Booking.check_in.desc()).all()
    return jsonify([booking.to_dict() for booking in bookings]), 200


@bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Obtener una reserva por ID"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    
    booking = db.session.get(Booking, booking_id)
    
    if not booking:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    
    # Si es cliente, solo puede ver sus propias reservas
    if user.role == 'cliente' and booking.user_id != user_id:
        return jsonify({'error': 'No tienes permisos para ver esta reserva'}), 403
    
    return jsonify(booking.to_dict()), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def create_booking():
    """Crear nueva reserva"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['room_id', 'check_in', 'check_out']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    # Verificar que la habitación existe
    room = db.session.get(Room, data['room_id'])
    if not room:
        return jsonify({'error': 'Habitación no encontrada'}), 404
    
    if not room.activo:
        return jsonify({'error': 'Habitación no disponible'}), 400
    
    # Parsear fechas
    try:
        check_in = datetime.strptime(data['check_in'], '%Y-%m-%d'). date()
        check_out = datetime.strptime(data['check_out'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido.  Use YYYY-MM-DD'}), 400
    
    # Validar fechas
    if check_in >= check_out:
        return jsonify({'error': 'La fecha de salida debe ser posterior a la de entrada'}), 400
    
    if check_in < datetime.now().date():
        return jsonify({'error': 'La fecha de entrada no puede ser en el pasado'}), 400
    
    # Calcular noches
    noches = (check_out - check_in).days
    
    # Verificar disponibilidad
    if not check_room_availability(data['room_id'], check_in, check_out):
        return jsonify({'error': 'La habitación no está disponible en esas fechas'}), 400
    
    # Calcular precios
    precio_por_noche = room.room_type.precio_base
    precio_servicios_extra = data.get('precio_servicios_extra', 0)
    precio_total = (precio_por_noche * noches) + precio_servicios_extra
    
    # Determinar el user_id (admin/trabajador puede crear reserva para otro usuario)
    target_user_id = user_id
    if user.role in ['admin', 'trabajador'] and 'user_id' in data:
        target_user_id = data['user_id']
        # Verificar que el usuario existe
        if not db.session.get(User, target_user_id):
            return jsonify({'error': 'Usuario no encontrado'}), 404
    
    booking = Booking(
        user_id=target_user_id,
        room_id=data['room_id'],
        check_in=check_in,
        check_out=check_out,
        noches=noches,
        precio_por_noche=precio_por_noche,
        precio_servicios_extra=precio_servicios_extra,
        precio_total=precio_total,
        estado=data.get('estado', 'pendiente'),
        metodo_pago=data.get('metodo_pago', 'presencial'),
        notas_especiales=data.get('notas_especiales')
    )
    
    try:
        db.session.add(booking)
        db.session.commit()
        return jsonify({
            'message': 'Reserva creada exitosamente',
            'booking': booking.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    """Actualizar reserva"""
    user_id = int(get_jwt_identity())
    user = db.session. get(User, user_id)
    
    booking = db. session.get(Booking, booking_id)
    
    if not booking:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    
    # Si es cliente, solo puede modificar sus propias reservas pendientes
    if user.role == 'cliente':
        if booking.user_id != user_id:
            return jsonify({'error': 'No tienes permisos para modificar esta reserva'}), 403
        if booking.estado not in ['pendiente']:
            return jsonify({'error': 'Solo puedes modificar reservas pendientes'}), 400
    
    data = request. get_json()
    
    # Actualizar fechas si se proporcionan
    if 'check_in' in data or 'check_out' in data:
        try:
            check_in = datetime.strptime(data. get('check_in', booking.check_in. isoformat()), '%Y-%m-%d').date()
            check_out = datetime.strptime(data.get('check_out', booking.check_out.isoformat()), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        if check_in >= check_out:
            return jsonify({'error': 'La fecha de salida debe ser posterior a la de entrada'}), 400
        
        # Verificar disponibilidad (excluyendo esta reserva)
        if not check_room_availability(booking.room_id, check_in, check_out, exclude_booking_id=booking_id):
            return jsonify({'error': 'La habitación no está disponible en esas fechas'}), 400
        
        booking.check_in = check_in
        booking.check_out = check_out
        booking.noches = (check_out - check_in).days
        
        # Recalcular precio total
        booking.precio_total = (booking. precio_por_noche * booking.noches) + booking.precio_servicios_extra
    
    # Admin/trabajador puede cambiar estado
    if user.role in ['admin', 'trabajador'] and 'estado' in data:
        booking. estado = data['estado']
    
    if 'notas_especiales' in data:
        booking.notas_especiales = data['notas_especiales']
    
    if 'precio_servicios_extra' in data:
        booking.precio_servicios_extra = data['precio_servicios_extra']
        booking.precio_total = (booking. precio_por_noche * booking.noches) + booking.precio_servicios_extra
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Reserva actualizada exitosamente',
            'booking': booking. to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:booking_id>/cancelar', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancelar reserva"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    
    booking = db.session.get(Booking, booking_id)
    
    if not booking:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    
    # Si es cliente, solo puede cancelar sus propias reservas
    if user.role == 'cliente' and booking.user_id != user_id:
        return jsonify({'error': 'No tienes permisos para cancelar esta reserva'}), 403
    
    if booking.estado == 'cancelada':
        return jsonify({'error': 'La reserva ya está cancelada'}), 400
    
    if booking.estado == 'check_out_realizado':
        return jsonify({'error': 'No se puede cancelar una reserva finalizada'}), 400
    
    booking.estado = 'cancelada'
    booking.fecha_cancelacion = datetime. utcnow()
    booking.cancelado_por_id = user_id
    
    db.session.commit()
    
    return jsonify({
        'message': 'Reserva cancelada exitosamente',
        'booking': booking.to_dict()
    }), 200


@bp.route('/<int:booking_id>/check-in', methods=['POST'])
@jwt_required()
@role_required('admin', 'trabajador')
def check_in(booking_id):
    """Realizar check-in (admin/trabajador)"""
    user_id = int(get_jwt_identity())
    
    booking = db.session.get(Booking, booking_id)
    
    if not booking:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    
    if booking.estado != 'confirmada':
        return jsonify({'error': 'Solo se puede hacer check-in de reservas confirmadas'}), 400
    
    booking.estado = 'check_in_realizado'
    booking. fecha_check_in_real = datetime.utcnow()
    booking.check_in_realizado_por_id = user_id
    
    # Cambiar estado de la habitación
    room = db.session.get(Room, booking.room_id)
    room.estado = 'ocupada'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Check-in realizado exitosamente',
        'booking': booking.to_dict()
    }), 200


@bp.route('/<int:booking_id>/check-out', methods=['POST'])
@jwt_required()
@role_required('admin', 'trabajador')
def check_out(booking_id):
    """Realizar check-out (admin/trabajador)"""
    user_id = int(get_jwt_identity())
    
    booking = db.session.get(Booking, booking_id)
    
    if not booking:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    
    if booking.estado != 'check_in_realizado':
        return jsonify({'error': 'Solo se puede hacer check-out después del check-in'}), 400
    
    booking.estado = 'check_out_realizado'
    booking.fecha_check_out_real = datetime.utcnow()
    booking. check_out_realizado_por_id = user_id
    
    # Cambiar estado de la habitación
    room = db.session.get(Room, booking.room_id)
    room.estado = 'limpieza'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Check-out realizado exitosamente',
        'booking': booking.to_dict()
    }), 200


@bp.route('/disponibilidad', methods=['GET'])
def check_availability():
    """Verificar disponibilidad de habitaciones en un rango de fechas"""
    check_in_str = request.args.get('check_in')
    check_out_str = request.args.get('check_out')
    room_type_id = request.args.get('tipo')
    
    if not check_in_str or not check_out_str:
        return jsonify({'error': 'Los parámetros check_in y check_out son requeridos'}), 400
    
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d'). date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
    
    # Obtener todas las habitaciones
    query = Room.query. filter_by(activo=True)
    if room_type_id:
        query = query.filter_by(room_type_id=room_type_id)
    
    all_rooms = query.all()
    
    # Filtrar las disponibles
    available_rooms = []
    for room in all_rooms:
        if check_room_availability(room.id, check_in, check_out):
            available_rooms.append(room. to_dict())
    
    return jsonify({
        'check_in': check_in. isoformat(),
        'check_out': check_out.isoformat(),
        'total_disponibles': len(available_rooms),
        'habitaciones': available_rooms
    }), 200