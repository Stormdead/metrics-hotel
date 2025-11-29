from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app. models.booking import Booking
from app.models.room import Room, RoomType
from app.models.user import User
from app.utils.decorators import role_required
from datetime import datetime, timedelta
from sqlalchemy import func, extract

bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('admin', 'trabajador')
def get_dashboard():
    """Obtener métricas generales del dashboard"""
    # Parámetros de filtro (opcional)
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args. get('fecha_fin')
    
    # Por defecto, últimos 30 días
    if not fecha_inicio_str or not fecha_fin_str:
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
    else:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
    
    # Total de habitaciones
    total_habitaciones = Room.query.filter_by(activo=True).count()
    
    # Habitaciones por estado
    habitaciones_disponibles = Room.query.filter_by(estado='disponible', activo=True).count()
    habitaciones_ocupadas = Room.query.filter_by(estado='ocupada', activo=True).count()
    habitaciones_limpieza = Room.query. filter_by(estado='limpieza', activo=True).count()
    habitaciones_mantenimiento = Room. query.filter_by(estado='mantenimiento', activo=True).count()
    
    # Tasa de ocupación actual
    tasa_ocupacion = (habitaciones_ocupadas / total_habitaciones * 100) if total_habitaciones > 0 else 0
    
    # Reservas en el período
    reservas_periodo = Booking.query.filter(
        Booking.check_in >= fecha_inicio,
        Booking.check_in <= fecha_fin
    ).all()
    
    # Total de reservas por estado
    reservas_pendientes = len([b for b in reservas_periodo if b.estado == 'pendiente'])
    reservas_confirmadas = len([b for b in reservas_periodo if b.estado == 'confirmada'])
    reservas_check_in = len([b for b in reservas_periodo if b. estado == 'check_in_realizado'])
    reservas_completadas = len([b for b in reservas_periodo if b.estado == 'check_out_realizado'])
    reservas_canceladas = len([b for b in reservas_periodo if b.estado == 'cancelada'])
    
    # Ingresos totales (solo reservas completadas)
    ingresos_totales = sum([b.precio_total for b in reservas_periodo if b.estado == 'check_out_realizado'])
    
    # Ingresos proyectados (reservas confirmadas + check-in)
    ingresos_proyectados = sum([b.precio_total for b in reservas_periodo if b.estado in ['confirmada', 'check_in_realizado']])
    
    # Total de clientes
    total_clientes = User.query.filter_by(role='cliente', activo=True).count()
    
    # Clientes nuevos en el período
    clientes_nuevos = User.query.filter(
        User.role == 'cliente',
        User.fecha_creacion >= datetime.combine(fecha_inicio, datetime.min.time()),
        User.fecha_creacion <= datetime.combine(fecha_fin, datetime.max.time())
    ).count()
    
    return jsonify({
        'periodo': {
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat()
        },
        'habitaciones': {
            'total': total_habitaciones,
            'disponibles': habitaciones_disponibles,
            'ocupadas': habitaciones_ocupadas,
            'limpieza': habitaciones_limpieza,
            'mantenimiento': habitaciones_mantenimiento,
            'tasa_ocupacion': round(tasa_ocupacion, 2)
        },
        'reservas': {
            'total': len(reservas_periodo),
            'pendientes': reservas_pendientes,
            'confirmadas': reservas_confirmadas,
            'check_in_realizado': reservas_check_in,
            'completadas': reservas_completadas,
            'canceladas': reservas_canceladas
        },
        'ingresos': {
            'totales': float(ingresos_totales),
            'proyectados': float(ingresos_proyectados)
        },
        'clientes': {
            'total': total_clientes,
            'nuevos_periodo': clientes_nuevos
        }
    }), 200


@bp.route('/ocupacion', methods=['GET'])
@jwt_required()
@role_required('admin', 'trabajador')
def get_ocupacion():
    """Obtener tasa de ocupación por día en un rango de fechas"""
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    if not fecha_inicio_str or not fecha_fin_str:
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
    else:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
    
    total_habitaciones = Room.query. filter_by(activo=True).count()
    
    ocupacion_diaria = []
    fecha_actual = fecha_inicio
    
    while fecha_actual <= fecha_fin:
        # Contar reservas activas en esta fecha
        reservas_activas = Booking.query.filter(
            Booking.check_in <= fecha_actual,
            Booking.check_out > fecha_actual,
            Booking.estado. in_(['confirmada', 'check_in_realizado'])
        ).count()
        
        tasa = (reservas_activas / total_habitaciones * 100) if total_habitaciones > 0 else 0
        
        ocupacion_diaria.append({
            'fecha': fecha_actual.isoformat(),
            'habitaciones_ocupadas': reservas_activas,
            'tasa_ocupacion': round(tasa, 2)
        })
        
        fecha_actual += timedelta(days=1)
    
    return jsonify({
        'periodo': {
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat()
        },
        'total_habitaciones': total_habitaciones,
        'ocupacion_diaria': ocupacion_diaria
    }), 200


@bp.route('/ingresos', methods=['GET'])
@jwt_required()
@role_required('admin', 'trabajador')
def get_ingresos():
    """Obtener ingresos por día/mes"""
    periodo = request.args.get('periodo', 'dia')
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    if not fecha_inicio_str or not fecha_fin_str:
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
    else:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
    
    if periodo == 'dia':
        ingresos_por_dia = []
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            # Ingresos de reservas completadas en este día
            ingresos = db.session.query(func.sum(Booking.precio_total)).filter(
                func.date(Booking.fecha_check_out_real) == fecha_actual,
                Booking.estado == 'check_out_realizado'
            ).scalar() or 0
            
            # Reservas completadas
            reservas = Booking.query.filter(
                func.date(Booking.fecha_check_out_real) == fecha_actual,
                Booking. estado == 'check_out_realizado'
            ).count()
            
            ingresos_por_dia.append({
                'fecha': fecha_actual.isoformat(),
                'ingresos': float(ingresos),
                'reservas_completadas': reservas
            })
            
            fecha_actual += timedelta(days=1)
        
        return jsonify({
            'periodo': 'dia',
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat(),
            'datos': ingresos_por_dia
        }), 200
    
    elif periodo == 'mes':
        # Agrupar por mes
        ingresos_por_mes = db.session.query(
            extract('year', Booking.fecha_check_out_real). label('año'),
            extract('month', Booking.fecha_check_out_real).label('mes'),
            func.sum(Booking.precio_total).label('ingresos'),
            func.count(Booking.id).label('reservas')
        ).filter(
            Booking.fecha_check_out_real >= datetime.combine(fecha_inicio, datetime.min.time()),
            Booking. fecha_check_out_real <= datetime.combine(fecha_fin, datetime.max.time()),
            Booking.estado == 'check_out_realizado'
        ).group_by('año', 'mes').all()
        
        datos = [{
            'año': int(row. año),
            'mes': int(row.mes),
            'ingresos': float(row. ingresos),
            'reservas_completadas': row.reservas
        } for row in ingresos_por_mes]
        
        return jsonify({
            'periodo': 'mes',
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat(),
            'datos': datos
        }), 200
    
    else:
        return jsonify({'error': 'Periodo inválido.  Use "dia" o "mes"'}), 400


@bp.route('/habitaciones-populares', methods=['GET'])
@jwt_required()
@role_required('admin', 'trabajador')
def get_habitaciones_populares():
    """Obtener las habitaciones más reservadas"""
    limite = request.args.get('limite', 10, type=int)
    
    habitaciones_populares = db.session.query(
        Room.id,
        Room.numero_habitacion,
        RoomType.nombre. label('tipo_nombre'),
        func.count(Booking.id). label('total_reservas')
    ).join(Booking, Booking.room_id == Room. id)\
     .join(RoomType, Room.room_type_id == RoomType.id)\
     . filter(Booking.estado. in_(['confirmada', 'check_in_realizado', 'check_out_realizado']))\
     .group_by(Room.id, Room.numero_habitacion, RoomType.nombre)\
     .order_by(func.count(Booking.id).desc())\
     .limit(limite). all()
    
    datos = [{
        'habitacion_id': row.id,
        'numero_habitacion': row.numero_habitacion,
        'tipo': row.tipo_nombre,
        'total_reservas': row. total_reservas
    } for row in habitaciones_populares]
    
    return jsonify({
        'habitaciones_populares': datos
    }), 200


@bp.route('/clientes-frecuentes', methods=['GET'])
@jwt_required()
@role_required('admin', 'trabajador')
def get_clientes_frecuentes():
    """Obtener los clientes con más reservas"""
    limite = request.args.get('limite', 10, type=int)
    
    clientes_frecuentes = db.session.query(
        User.id,
        User.nombre_completo,
        User.email,
        func.count(Booking.id). label('total_reservas'),
        func.sum(Booking.precio_total).label('total_gastado')
    ).join(Booking, Booking.user_id == User.id)\
     . filter(
         User.role == 'cliente',
         Booking.estado == 'check_out_realizado'
     )\
     .group_by(User.id, User.nombre_completo, User.email)\
     .order_by(func. count(Booking.id).desc())\
     .limit(limite). all()
    
    datos = [{
        'cliente_id': row.id,
        'nombre': row.nombre_completo,
        'email': row.email,
        'total_reservas': row.total_reservas,
        'total_gastado': float(row.total_gastado or 0)
    } for row in clientes_frecuentes]
    
    return jsonify({
        'clientes_frecuentes': datos
    }), 200


@bp.route('/tipos-habitacion-populares', methods=['GET'])
@jwt_required()
@role_required('admin', 'trabajador')
def get_tipos_populares():
    """Obtener los tipos de habitación más reservados"""
    tipos_populares = db.session.query(
        RoomType.id,
        RoomType.nombre,
        func.count(Booking.id).label('total_reservas'),
        func.sum(Booking.precio_total).label('ingresos_totales')
    ).join(Room, Room.room_type_id == RoomType.id)\
     .join(Booking, Booking.room_id == Room.id)\
     .filter(Booking.estado == 'check_out_realizado')\
     .group_by(RoomType.id, RoomType.nombre)\
     . order_by(func.count(Booking.id).desc()). all()
    
    datos = [{
        'tipo_id': row.id,
        'nombre': row.nombre,
        'total_reservas': row.total_reservas,
        'ingresos_totales': float(row.ingresos_totales or 0)
    } for row in tipos_populares]
    
    return jsonify({
        'tipos_populares': datos
    }), 200