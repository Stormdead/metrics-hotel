import pytest

def test_get_current_user(client):
    """Test: Obtener información del usuario actual"""
    # Registrar y obtener token
    register_response = client. post('/api/auth/register', json={
        'email': 'current@test.com',
        'password': 'password123',
        'nombre_completo': 'Current User',
        'rut': '88888888-8'
    })
    token = register_response.json['access_token']
    
    # Obtener info del usuario
    response = client.get('/api/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    
    # DEBUG: Ver qué devuelve
    print(f"\n\nStatus: {response.status_code}")
    print(f"Response: {response.json}")
    
    assert response.status_code == 200
    assert response.json['email'] == 'current@test.com'

def test_register_success(client):
    """Test: Registro exitoso de cliente"""
    response = client.post('/api/auth/register', json={
        'email': 'cliente@test.com',
        'password': 'password123',
        'nombre_completo': 'Cliente Test',
        'rut': '22222222-2',
        'edad': 25,
        'telefono': '+56912345678'
    })
    
    assert response.status_code == 201
    assert 'access_token' in response.json
    assert response.json['user']['role'] == 'cliente'
    assert response.json['user']['email'] == 'cliente@test.com'

def test_register_duplicate_email(client):
    """Test: Registro con email duplicado"""
    # Primer registro
    client.post('/api/auth/register', json={
        'email': 'test@test.com',
        'password': 'password123',
        'nombre_completo': 'Test User',
        'rut': '33333333-3'
    })
    
    # Segundo registro con mismo email
    response = client.post('/api/auth/register', json={
        'email': 'test@test.com',
        'password': 'password123',
        'nombre_completo': 'Test User 2',
        'rut': '44444444-4'
    })
    
    assert response.status_code == 400
    assert 'email ya está registrado' in response.json['error']

def test_register_duplicate_rut(client):
    """Test: Registro con RUT duplicado"""
    # Primer registro
    client.post('/api/auth/register', json={
        'email': 'test1@test.com',
        'password': 'password123',
        'nombre_completo': 'Test User',
        'rut': '55555555-5'
    })
    
    # Segundo registro con mismo RUT
    response = client.post('/api/auth/register', json={
        'email': 'test2@test. com',
        'password': 'password123',
        'nombre_completo': 'Test User 2',
        'rut': '55555555-5'
    })
    
    assert response.status_code == 400
    assert 'RUT ya está registrado' in response.json['error']

def test_register_missing_fields(client):
    """Test: Registro con campos faltantes"""
    response = client.post('/api/auth/register', json={
        'email': 'test@test.com',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    assert 'requerido' in response.json['error']

def test_login_success(client):
    """Test: Login exitoso"""
    # Registrar usuario
    client. post('/api/auth/register', json={
        'email': 'login@test.com',
        'password': 'password123',
        'nombre_completo': 'Login Test',
        'rut': '66666666-6'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'login@test.com',
        'password': 'password123'
    })
    
    assert response. status_code == 200
    assert 'access_token' in response.json
    assert response. json['user']['email'] == 'login@test.com'

def test_login_invalid_credentials(client):
    """Test: Login con credenciales inválidas"""
    response = client.post('/api/auth/login', json={
        'email': 'noexiste@test.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert 'Credenciales inválidas' in response.json['error']

def test_login_wrong_password(client):
    """Test: Login con contraseña incorrecta"""
    # Registrar usuario
    client.post('/api/auth/register', json={
        'email': 'test@test.com',
        'password': 'correctpassword',
        'nombre_completo': 'Test User',
        'rut': '77777777-7'
    })
    
    # Login con contraseña incorrecta
    response = client.post('/api/auth/login', json={
        'email': 'test@test.com',
        'password': 'wrongpassword'
    })
    
    assert response. status_code == 401
    assert 'Credenciales inválidas' in response.json['error']

def test_get_current_user(client):
    """Test: Obtener información del usuario actual"""
    # Registrar y obtener token
    register_response = client.post('/api/auth/register', json={
        'email': 'current@test.com',
        'password': 'password123',
        'nombre_completo': 'Current User',
        'rut': '88888888-8'
    })
    token = register_response.json['access_token']
    
    # Obtener info del usuario
    response = client. get('/api/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    
    assert response.status_code == 200
    assert response. json['email'] == 'current@test.com'

def test_change_password_success(client):
    """Test: Cambio de contraseña exitoso"""
    # Registrar y obtener token
    register_response = client.post('/api/auth/register', json={
        'email': 'changepass@test.com',
        'password': 'oldpassword',
        'nombre_completo': 'Change Pass User',
        'rut': '99999999-9'
    })
    token = register_response.json['access_token']
    
    # Cambiar contraseña
    response = client. post('/api/auth/change-password', 
        headers={'Authorization': f'Bearer {token}'},
        json={
            'current_password': 'oldpassword',
            'new_password': 'newpassword123'
        }
    )
    
    assert response.status_code == 200
    assert 'Contraseña actualizada exitosamente' in response.json['message']
    
    # Verificar que puede hacer login con nueva contraseña
    login_response = client.post('/api/auth/login', json={
        'email': 'changepass@test.com',
        'password': 'newpassword123'
    })
    assert login_response.status_code == 200

def test_change_password_wrong_current(client):
    """Test: Cambio de contraseña con contraseña actual incorrecta"""
    # Registrar y obtener token
    register_response = client.post('/api/auth/register', json={
        'email': 'wrongpass@test.com',
        'password': 'password123',
        'nombre_completo': 'Wrong Pass User',
        'rut': '10101010-1'
    })
    token = register_response.json['access_token']
    
    # Intentar cambiar contraseña con contraseña actual incorrecta
    response = client.post('/api/auth/change-password', 
        headers={'Authorization': f'Bearer {token}'},
        json={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
    )
    
    assert response.status_code == 401
    assert 'Contraseña actual incorrecta' in response.json['error']