from app import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db. Integer, primary_key=True)
    user_id = db. Column(db.Integer, db. ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db. Integer, db.ForeignKey('rooms.id'), nullable=False)
    
    # Fechas
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    noches = db.Column(db. Integer, nullable=False)
    
    # Precios
    precio_por_noche = db.Column(db.Numeric(10, 2), nullable=False)
    precio_servicios_extra = db.Column(db. Numeric(10, 2), default=0)
    precio_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Estado de la reserva
    estado = db.Column(
        db. Enum('pendiente', 'confirmada', 'check_in_realizado', 'check_out_realizado', 'cancelada'),
        default='pendiente',
        nullable=False
    )
    
    # Pago
    metodo_pago = db.Column(db.String(50), nullable=False, default='presencial')
    pagado = db.Column(db. Boolean, default=False)
    monto_pagado = db.Column(db.Numeric(10, 2), default=0)
    
    # Información adicional
    notas_especiales = db.Column(db. Text)
    
    # Timestamps
    fecha_reserva = db.Column(db. DateTime, default=datetime.utcnow)
    fecha_cancelacion = db.Column(db. DateTime)
    fecha_check_in_real = db.Column(db.DateTime)
    fecha_check_out_real = db.Column(db.DateTime)
    
    # Quién realizó acciones
    cancelado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    check_in_realizado_por_id = db.Column(db. Integer, db.ForeignKey('users.id'))
    check_out_realizado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relaciones
    user = db.relationship('User', foreign_keys=[user_id], back_populates='bookings')
    room = db.relationship('Room', back_populates='bookings')
    cancelado_por = db.relationship('User', foreign_keys=[cancelado_por_id])
    check_in_realizado_por = db.relationship('User', foreign_keys=[check_in_realizado_por_id])
    check_out_realizado_por = db.relationship('User', foreign_keys=[check_out_realizado_por_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'room_id': self.room_id,
            'room': self.room.to_dict() if self.room else None,
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'noches': self.noches,
            'precio_por_noche': float(self.precio_por_noche),
            'precio_servicios_extra': float(self.precio_servicios_extra),
            'precio_total': float(self.precio_total),
            'estado': self.estado,
            'metodo_pago': self.metodo_pago,
            'pagado': self.pagado,
            'monto_pagado': float(self.monto_pagado),
            'notas_especiales': self.notas_especiales,
            'fecha_reserva': self.fecha_reserva.isoformat() if self.fecha_reserva else None,
            'fecha_cancelacion': self.fecha_cancelacion.isoformat() if self.fecha_cancelacion else None,
            'fecha_check_in_real': self.fecha_check_in_real.isoformat() if self.fecha_check_in_real else None,
            'fecha_check_out_real': self.fecha_check_out_real.isoformat() if self.fecha_check_out_real else None
        }
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.estado}>'