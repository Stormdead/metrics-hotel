import os
from app import create_app, db
from app.models. user import User
from app.models.room import Room, RoomType
from app.models.booking import Booking

# Crear la aplicación
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

# Shell context para Flask CLI
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Room': Room,
        'RoomType': RoomType,
        'Booking': Booking
    }

# Comando para crear las tablas
@app.cli. command()
def create_db():
    """Crear todas las tablas de la base de datos"""
    db.create_all()
    print(" Base de datos creada exitosamente")

# Comando para crear usuario admin por defecto
@app.cli. command()
def create_admin():
    """Crear usuario administrador por defecto"""
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(email='admin@metricshotel.com').first()
    if admin:
        print(" El usuario admin ya existe")
        return
    
    admin = User(
        email='admin@metricshotel.com',
        password_hash=generate_password_hash('admin123'),
        role='admin',
        nombre_completo='Administrador del Sistema',
        rut='11111111-1',
        edad=30,
        telefono='+56912345678',
        activo=True
    )
    
    db.session.add(admin)
    db.session.commit()
    print(" Usuario admin creado exitosamente")
    print("   Email: admin@metricshotel.com")
    print("   Password: admin123")

if __name__ == '__main__':
    app.run(debug=True, port=5000)