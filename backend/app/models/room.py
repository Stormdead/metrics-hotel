from app import db
from datetime import datetime

class RoomType(db.Model):
    __tablename__ = 'room_types'
    
    id = db.Column(db. Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    capacidad_personas = db.Column(db.Integer, nullable=False)
    precio_base = db.Column(db. Numeric(10, 2), nullable=False)
    amenidades = db.Column(db.JSON)  # ["TV", "AC", "Minibar"]
    imagenes = db.Column(db. JSON)    # ["url1", "url2"]
    activo = db.Column(db. Boolean, default=True)
    
    # Relaciones
    rooms = db.relationship('Room', back_populates='room_type', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self. descripcion,
            'capacidad_personas': self.capacidad_personas,
            'precio_base': float(self.precio_base),
            'amenidades': self.amenidades or [],
            'imagenes': self.imagenes or [],
            'activo': self.activo,
            'cantidad_habitaciones': self.rooms.count()
        }
    
    def __repr__(self):
        return f'<RoomType {self.nombre}>'


class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.id'), nullable=False)
    numero_habitacion = db.Column(db.String(10), unique=True, nullable=False)
    piso = db.Column(db. Integer)
    estado = db.Column(
        db.Enum('disponible', 'ocupada', 'limpieza', 'mantenimiento'),
        default='disponible',
        nullable=False
    )
    activo = db.Column(db. Boolean, default=True)
    
    # Relaciones
    room_type = db.relationship('RoomType', back_populates='rooms')
    bookings = db.relationship('Booking', back_populates='room', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_type_id': self.room_type_id,
            'room_type': self.room_type.to_dict() if self.room_type else None,
            'numero_habitacion': self.numero_habitacion,
            'piso': self. piso,
            'estado': self.estado,
            'activo': self.activo
        }
    
    def __repr__(self):
        return f'<Room {self.numero_habitacion} - {self.estado}>'