from app import create_app, db
from app. models. user import User

app = create_app()

with app.app_context():
    # Verificar si ya existe
    existing = User.query.filter_by(email='admin@metricshotel. com').first()
    
    if existing:
        print('El admin ya existe')
    else:
        # Crear admin
        admin = User(
            email='admin@metricshotel.com',
            nombre_completo='Administrador',
            rut='11111111-1',
            role='admin',
            activo=True,
            debe_cambiar_password=False
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print('✅ Admin creado exitosamente')
        print('Email: admin@metricshotel.com')
        print('Password: admin123')