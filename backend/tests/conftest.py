import pytest
import os
from app import create_app, db
from app.models. user import User

# Configuración de testing
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

@pytest.fixture(scope='function')
def app():
    """Crear aplicación para tests"""
    # Configurar para testing
    app = create_app('default')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario admin de prueba
        admin = User(
            email='admin@test.com',
            role='admin',
            nombre_completo='Admin Test',
            rut='admin-test-rut',
            edad=30,
            activo=True
        )
        admin.set_password('admin123')
        
        try:
            db.session.add(admin)
            db.session.commit()
        except Exception as e:
            db.session. rollback()
            print(f"Error creando admin en tests: {e}")
        
        yield app
        
        # Limpiar después de cada test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de test"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def admin_token(client):
    """Token de admin para tests"""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    
    if response.status_code != 200:
        print(f"Error en login de admin: {response.json}")
        return None
    
    return response. json['access_token']