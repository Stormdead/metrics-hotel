import requests

BASE_URL = "http://localhost:5000/api"

print("=== TEST REGISTRO ===")
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "nuevo@test.com",  # Cambiar email para evitar duplicados
    "password": "password123",
    "nombre_completo": "Nuevo Usuario",
    "rut": "11223344-5"
})
print(f"Status: {response.status_code}")

if response.status_code == 201:
    data = response.json()
    print(f"✅ Usuario creado: {data['user']['email']}")
    token = data['access_token']
else:
    print(f"Response: {response.json()}")
    # Si falla, hacer login
    print("\n=== LOGIN CON USUARIO EXISTENTE ===")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@test.com",
        "password": "password123"
    })
    token = response.json(). get('access_token')

# Test: Obtener usuario actual
print("\n=== TEST GET ME ===")
headers = {"Authorization": f"Bearer {token}"}
response = requests. get(f"{BASE_URL}/auth/me", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Usuario actual: {response. json()['email']}")
else:
    print(f"❌ Error: {response.json()}")

# Test: Cambiar contraseña
print("\n=== TEST CAMBIAR CONTRASEÑA ===")
response = requests.post(f"{BASE_URL}/auth/change-password", 
    headers=headers,
    json={
        "current_password": "password123",
        "new_password": "newpassword456"
    }
)
print(f"Status: {response. status_code}")
if response. status_code == 200:
    print(f"✅ Contraseña cambiada")
else:
    print(f"Response: {response.json()}")

# Test: Login con admin
print("\n=== TEST LOGIN ADMIN ===")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "admin@metricshotel.com",
    "password": "admin123"
})
print(f"Status: {response. status_code}")
admin_token = response.json().get('access_token')
if admin_token:
    print(f"✅ Admin token obtenido")

# Test: Listar usuarios
print("\n=== TEST LISTAR USUARIOS ===")
headers = {"Authorization": f"Bearer {admin_token}"}
response = requests.get(f"{BASE_URL}/users/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    users = response.json()
    print(f"✅ Total usuarios: {len(users)}")
    for user in users:
        print(f"  - {user['email']} ({user['role']})")
else:
    print(f"❌ Error: {response.json()}")

# Test: Crear trabajador
print("\n=== TEST CREAR TRABAJADOR ===")
response = requests.post(f"{BASE_URL}/users/create-worker", 
    headers=headers, 
    json={
        "nombre_completo": "María González",
        "rut": "22334455-6",
        "role": "trabajador",
        "edad": 25,
        "telefono": "+56987654321"
    }
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"✅ Trabajador creado:")
    print(f"  Email: {data['credentials']['email']}")
    print(f"  Password temporal: {data['credentials']['password']}")
else:
    print(f"Response: {response.json()}")

# Test: Crear admin
print("\n=== TEST CREAR ADMIN ===")
response = requests.post(f"{BASE_URL}/users/create-worker", 
    headers=headers, 
    json={
        "nombre_completo": "Carlos Admin",
        "rut": "33445566-7",
        "role": "admin",
        "edad": 35
    }
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"✅ Admin creado:")
    print(f"  Email: {data['credentials']['email']}")
    print(f"  Password temporal: {data['credentials']['password']}")
else:
    print(f"Response: {response.json()}")

print("\n" + "="*50)
print("✅ TODOS LOS TESTS COMPLETADOS")
print("="*50)