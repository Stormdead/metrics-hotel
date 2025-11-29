import pytest

def test_create_worker_success(client, admin_token):
    """Test: Crear trabajador exitosamente"""
    response = client. post('/api/users/create-worker',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'nombre_completo': 'Juan Perez',
            'rut': '12345678-9',
            'role': 'trabajador',
            'edad': 28,
            'telefono': '+56987654321'
        }
    )
    
    assert response.status_code == 201
    assert 'credentials' in response.json
    assert 'email' in response.json['credentials']
    assert '@metricshotel.com' in response.json['credentials']['email']
    assert response.json['user']['role'] == 'trabajador'
    assert response.json['user']['debe_cambiar_password'] == True

def test_create_admin_success(client, admin_token):
    """Test: Crear administrador exitosamente"""
    response = client.post('/api/users/create-worker',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'nombre_completo': 'Admin Nuevo',
            'rut': '98765432-1',
            'role': 'admin',
            'edad': 35
        }
    )
    
    assert response.status_code == 201
    assert response.json['user']['role'] == 'admin'

def test_create_worker_duplicate_rut(client, admin_token):
    """Test: No permitir RUT duplicado"""
    # Crear primer trabajador
    client.post('/api/users/create-worker',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'nombre_completo': 'Trabajador Uno',
            'rut': '11111111-1',
            'role': 'trabajador'
        }
    )
    
    # Intentar crear segundo con mismo RUT
    response = client.post('/api/users/create-worker',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'nombre_completo': 'Trabajador Dos',
            'rut': '11111111-1',
            'role': 'trabajador'
        }
    )
    
    assert response.status_code == 400
    assert 'RUT ya está registrado' in response.json['error']

def test_create_worker_without_permission(client):
    """Test: Cliente no puede crear trabajadores"""
    # Registrar como cliente
    register_response = client.post('/api/auth/register', json={
        'email': 'cliente@test.com',
        'password': 'password123',
        'nombre_completo': 'Cliente Test',
        'rut': '22222222-2'
    })
    cliente_token = register_response.json['access_token']
    
    # Intentar crear trabajador
    response = client.post('/api/users/create-worker',
        headers={'Authorization': f'Bearer {cliente_token}'},
        json={
            'nombre_completo': 'Trabajador Test',
            'rut': '33333333-3',
            'role': 'trabajador'
        }
    )
    
    assert response.status_code == 403
    assert 'No tienes permisos' in response.json['error']

def test_get_users_list(client, admin_token):
    """Test: Obtener lista de usuarios"""
    response = client.get('/api/users/',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_deactivate_user(client, admin_token):
    """Test: Desactivar usuario"""
    # Crear trabajador
    create_response = client.post('/api/users/create-worker',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'nombre_completo': 'Trabajador Temporal',
            'rut': '44444444-4',
            'role': 'trabajador'
        }
    )
    user_id = create_response.json['user']['id']
    
    # Desactivar
    response = client. delete(f'/api/users/{user_id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    assert response.status_code == 200
    assert 'desactivado exitosamente' in response.json['message']