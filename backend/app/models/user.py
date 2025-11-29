from app import db
from datetime import datetime
from werkzeug. security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db. Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db. String(255), nullable=False)
    role = db.Column(db. Enum('cliente', 'trabajador', 'admin'), nullable=False, default='cliente')
    
    # Información personal
    nombre_completo = db.Column(db.String(200), nullable=False)
    rut = db.Column(db. String(20), unique=True, nullable=False, index=True)
    edad = db.Column(db.Integer)
    telefono = db.Column(db. String(20))
    direccion = db.Column(db. String(255))
    
    # Control de cuenta
    activo = db.Column(db. Boolean, default=True)
    debe_cambiar_password = db.Column(db.Boolean, default=False)
    
    # Relaciones
    creado_por_id = db.Column(db. Integer, db.ForeignKey('users.id'), nullable=True)
    creado_por = db.relationship('User', remote_side=[id], backref='usuarios_creados')
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime. utcnow)
    ultima_conexion = db.Column(db.DateTime)
    
    # Relaciones con otras tablas
    bookings = db.relationship('Booking', back_populates='user', lazy='dynamic', foreign_keys='Booking.user_id')
    
    def set_password(self, password):
        """Hashear la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convertir a diccionario"""
        data = {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'nombre_completo': self.nombre_completo,
            'rut': self.rut,
            'edad': self.edad,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'activo': self.activo,
            'debe_cambiar_password': self.debe_cambiar_password,
            'creado_por_id': self.creado_por_id,
            'fecha_creacion': self.fecha_creacion. isoformat() if self.fecha_creacion else None,
            'ultima_conexion': self.ultima_conexion.isoformat() if self.ultima_conexion else None
        }
        
        if include_sensitive:
            data['debe_cambiar_password'] = self.debe_cambiar_password
            data['creado_por_id'] = self.creado_por_id
        
        return data
    
    def __repr__(self):
        return f'<User {self.email} - {self.role}>'