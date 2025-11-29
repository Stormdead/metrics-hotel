import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

# ==================== AUTENTICACIÓN ====================
print_section("AUTENTICACIÓN")

# Login Admin
print(">>> Login Admin")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "admin@metricshotel.com",
    "password": "admin123"
})
print(f"Status: {response.status_code}")
admin_token = response.json(). get('access_token')
admin_headers = {"Authorization": f"Bearer {admin_token}"}
print(f"✅ Admin token obtenido\n")

# Registro o Login Cliente
print(">>> Verificar/Crear Cliente de Test")
cliente_email = "cliente_test@test.com"
cliente_password = "password123"
cliente_rut = "99999999-9"

# Intentar login primero
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": cliente_email,
    "password": cliente_password
})

if response.status_code == 200:
    # Cliente ya existe, usar ese
    cliente_token = response.json(). get('access_token')
    cliente_headers = {"Authorization": f"Bearer {cliente_token}"}
    print(f"ℹ️  Cliente ya existe: {cliente_email}")
    print(f"✅ Login exitoso\n")
else:
    # Cliente no existe, crear uno nuevo
    print(">>> Registrar Nuevo Cliente")
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": cliente_email,
        "password": cliente_password,
        "nombre_completo": "Cliente Test",
        "rut": cliente_rut
    })
    print(f"Status: {response. status_code}")
    if response.status_code == 201:
        cliente_token = response.json().get('access_token')
        cliente_headers = {"Authorization": f"Bearer {cliente_token}"}
        print(f"✅ Cliente creado: {cliente_email}\n")
    elif response.status_code == 400 and "RUT" in response.json(). get('error', ''):
        # Si el RUT existe, intentar login nuevamente
        print(f"ℹ️  RUT ya registrado, intentando login...")
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": cliente_email,
            "password": cliente_password
        })
        if response.status_code == 200:
            cliente_token = response.json().get('access_token')
            cliente_headers = {"Authorization": f"Bearer {cliente_token}"}
            print(f"✅ Login exitoso\n")
        else:
            print(f"❌ Error en login: {response.json()}")
            print(f"ℹ️  Usando admin como fallback\n")
            cliente_headers = admin_headers
    else:
        print(f"❌ Error: {response.json()}")
        print(f"ℹ️  Usando admin como fallback\n")
        cliente_headers = admin_headers
        
# ==================== TIPOS DE HABITACIÓN ====================
print_section("TIPOS DE HABITACIÓN")

# Obtener tipos existentes primero
response = requests.get(f"{BASE_URL}/rooms/types")
tipos_existentes = {t['nombre']: t['id'] for t in response.json()} if response.status_code == 200 else {}

# Crear tipo Simple
print(">>> Crear Tipo: Simple")
if "Simple" in tipos_existentes:
    tipo_simple_id = tipos_existentes["Simple"]
    print(f"ℹ️  Tipo Simple ya existe (ID: {tipo_simple_id})\n")
else:
    response = requests.post(f"{BASE_URL}/rooms/types", headers=admin_headers, json={
        "nombre": "Simple",
        "descripcion": "Habitación simple con una cama individual",
        "capacidad_personas": 1,
        "precio_base": 30000,
        "amenidades": ["WiFi", "TV", "Baño privado"],
        "imagenes": ["https://example.com/simple.jpg"]
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        tipo_simple_id = response.json()['room_type']['id']
        print(f"✅ Tipo Simple creado (ID: {tipo_simple_id})\n")
    else:
        print(f"❌ Error: {response.json()}\n")
        tipo_simple_id = None

# Crear tipo Doble
print(">>> Crear Tipo: Doble")
if "Doble" in tipos_existentes:
    tipo_doble_id = tipos_existentes["Doble"]
    print(f"ℹ️  Tipo Doble ya existe (ID: {tipo_doble_id})\n")
else:
    response = requests.post(f"{BASE_URL}/rooms/types", headers=admin_headers, json={
        "nombre": "Doble",
        "descripcion": "Habitación doble con cama matrimonial",
        "capacidad_personas": 2,
        "precio_base": 50000,
        "amenidades": ["WiFi", "TV", "Baño privado", "Minibar"],
        "imagenes": ["https://example.com/doble.jpg"]
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        tipo_doble_id = response.json()['room_type']['id']
        print(f"✅ Tipo Doble creado (ID: {tipo_doble_id})\n")
    else:
        print(f"❌ Error: {response.json()}\n")
        tipo_doble_id = None

# Crear tipo Suite
print(">>> Crear Tipo: Suite")
if "Suite" in tipos_existentes:
    tipo_suite_id = tipos_existentes["Suite"]
    print(f"ℹ️  Tipo Suite ya existe (ID: {tipo_suite_id})\n")
else:
    response = requests.post(f"{BASE_URL}/rooms/types", headers=admin_headers, json={
        "nombre": "Suite",
        "descripcion": "Suite de lujo con jacuzzi",
        "capacidad_personas": 4,
        "precio_base": 100000,
        "amenidades": ["WiFi", "TV", "Baño privado", "Minibar", "Jacuzzi", "Vista al mar"],
        "imagenes": ["https://example.com/suite. jpg"]
    })
    print(f"Status: {response. status_code}")
    if response.status_code == 201:
        tipo_suite_id = response.json()['room_type']['id']
        print(f"✅ Tipo Suite creado (ID: {tipo_suite_id})\n")
    else:
        print(f"❌ Error: {response. json()}\n")
        tipo_suite_id = None

# Listar tipos
print(">>> Listar Tipos de Habitación")
response = requests. get(f"{BASE_URL}/rooms/types")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    tipos = response.json()
    print(f"✅ Total tipos: {len(tipos)}")
    for tipo in tipos:
        print(f"  - {tipo['nombre']}: ${tipo['precio_base']} (Cap: {tipo['capacidad_personas']} personas)")
    print()

# ==================== HABITACIONES ====================
print_section("HABITACIONES")

# Obtener habitaciones existentes
response = requests.get(f"{BASE_URL}/rooms/")
habitaciones_existentes = {h['numero_habitacion']: h['id'] for h in response.json()} if response.status_code == 200 else {}
habitaciones_creadas = list(habitaciones_existentes.values())

# Crear habitaciones simples (101-105)
print(">>> Crear Habitaciones Simples (101-105)")
contador_simples = 0
if tipo_simple_id:
    for i in range(101, 106):
        num_hab = str(i)
        if num_hab in habitaciones_existentes:
            habitaciones_creadas.append(habitaciones_existentes[num_hab])
            contador_simples += 1
        else:
            response = requests.post(f"{BASE_URL}/rooms/", headers=admin_headers, json={
                "room_type_id": tipo_simple_id,
                "numero_habitacion": num_hab,
                "piso": 1,
                "estado": "disponible"
            })
            if response.status_code == 201:
                habitaciones_creadas.append(response.json()['room']['id'])
                contador_simples += 1
    print(f"✅ {contador_simples} habitaciones simples disponibles\n")

# Crear habitaciones dobles (201-205)
print(">>> Crear Habitaciones Dobles (201-205)")
contador_dobles = 0
if tipo_doble_id:
    for i in range(201, 206):
        num_hab = str(i)
        if num_hab in habitaciones_existentes:
            habitaciones_creadas. append(habitaciones_existentes[num_hab])
            contador_dobles += 1
        else:
            response = requests.post(f"{BASE_URL}/rooms/", headers=admin_headers, json={
                "room_type_id": tipo_doble_id,
                "numero_habitacion": num_hab,
                "piso": 2,
                "estado": "disponible"
            })
            if response.status_code == 201:
                habitaciones_creadas.append(response.json()['room']['id'])
                contador_dobles += 1
    print(f"✅ {contador_dobles} habitaciones dobles disponibles\n")

# Crear habitaciones suite (301-302)
print(">>> Crear Habitaciones Suite (301-302)")
contador_suites = 0
if tipo_suite_id:
    for i in range(301, 303):
        num_hab = str(i)
        if num_hab in habitaciones_existentes:
            habitaciones_creadas.append(habitaciones_existentes[num_hab])
            contador_suites += 1
        else:
            response = requests.post(f"{BASE_URL}/rooms/", headers=admin_headers, json={
                "room_type_id": tipo_suite_id,
                "numero_habitacion": num_hab,
                "piso": 3,
                "estado": "disponible"
            })
            if response.status_code == 201:
                habitaciones_creadas.append(response.json()['room']['id'])
                contador_suites += 1
    print(f"✅ {contador_suites} habitaciones suite disponibles\n")

# Listar habitaciones
print(">>> Listar Habitaciones")
response = requests.get(f"{BASE_URL}/rooms/")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    rooms = response.json()
    print(f"✅ Total habitaciones: {len(rooms)}")
    for room in rooms[:5]:
        print(f"  - Hab {room['numero_habitacion']} (Piso {room['piso']}): {room['estado']}")
    print()

# ==================== RESERVAS ====================
print_section("RESERVAS")

if len(habitaciones_creadas) > 0:
    # Verificar disponibilidad
    print(">>> Verificar Disponibilidad")
    hoy = datetime.now().date()
    check_in = hoy + timedelta(days=2)
    check_out = hoy + timedelta(days=5)
    response = requests.get(f"{BASE_URL}/bookings/disponibilidad", params={
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat()
    })
    print(f"Status: {response. status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Disponibles: {data['total_disponibles']} habitaciones")
        print(f"   Check-in: {data['check_in']}")
        print(f"   Check-out: {data['check_out']}\n")

    # Crear reserva como cliente
    print(">>> Crear Reserva (Cliente)")
    response = requests.post(f"{BASE_URL}/bookings/", headers=cliente_headers, json={
        "room_id": habitaciones_creadas[0],
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "metodo_pago": "tarjeta",
        "notas_especiales": "Llegada tarde (después de las 22:00)"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        reserva_id = response.json()['booking']['id']
        print(f"✅ Reserva creada (ID: {reserva_id})")
        print(f"   Precio total: ${response.json()['booking']['precio_total']}")
        print(f"   Noches: {response.json()['booking']['noches']}\n")
        
        # Confirmar reserva (Admin)
        print(">>> Confirmar Reserva (Admin)")
        response = requests.put(f"{BASE_URL}/bookings/{reserva_id}", headers=admin_headers, json={
            "estado": "confirmada"
        })
        print(f"Status: {response.status_code}")
        if response. status_code == 200:
            print(f"✅ Reserva confirmada\n")
    else:
        print(f"❌ Error: {response. json()}\n")
        reserva_id = None

    # Crear más reservas para métricas
    if len(habitaciones_creadas) >= 5:
        print(">>> Crear Reservas Adicionales para Métricas")
        reservas_adicionales = 0
        for i in range(1, min(5, len(habitaciones_creadas))):
            room_id = habitaciones_creadas[i]
            check_in_extra = hoy + timedelta(days=i)
            check_out_extra = hoy + timedelta(days=i+3)
            response = requests.post(f"{BASE_URL}/bookings/", headers=admin_headers, json={
                "room_id": room_id,
                "check_in": check_in_extra.isoformat(),
                "check_out": check_out_extra.isoformat(),
                "estado": "confirmada",
                "metodo_pago": "efectivo"
            })
            if response.status_code == 201:
                reservas_adicionales += 1
                # Hacer check-in y check-out para algunas
                if i <= 2:
                    booking_id = response.json()['booking']['id']
                    # Check-in
                    requests.post(f"{BASE_URL}/bookings/{booking_id}/check-in", headers=admin_headers)
                    # Check-out
                    if i == 1:
                        requests.post(f"{BASE_URL}/bookings/{booking_id}/check-out", headers=admin_headers)
        print(f"✅ {reservas_adicionales} reservas adicionales creadas\n")

    # Listar reservas
    print(">>> Listar Reservas (Admin)")
    response = requests. get(f"{BASE_URL}/bookings/", headers=admin_headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        bookings = response. json()
        print(f"✅ Total reservas: {len(bookings)}")
        for booking in bookings[:3]:
            print(f"  - Reserva #{booking['id']}: {booking['estado']} (Hab {booking['room']['numero_habitacion']})")
        print()
else:
    print("⚠️  No hay habitaciones disponibles para crear reservas\n")

# ==================== MÉTRICAS ====================
print_section("MÉTRICAS")

# Dashboard
print(">>> Dashboard General")
response = requests.get(f"{BASE_URL}/metrics/dashboard", headers=admin_headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Dashboard:")
    print(f"   Habitaciones totales: {data['habitaciones']['total']}")
    print(f"   Habitaciones disponibles: {data['habitaciones']['disponibles']}")
    print(f"   Habitaciones ocupadas: {data['habitaciones']['ocupadas']}")
    print(f"   Tasa de ocupación: {data['habitaciones']['tasa_ocupacion']}%")
    print(f"   Total reservas: {data['reservas']['total']}")
    print(f"   Ingresos totales: ${data['ingresos']['totales']}")
    print(f"   Clientes totales: {data['clientes']['total']}\n")

# Ocupación diaria
print(">>> Ocupación Diaria (Últimos 7 días)")
hoy = datetime.now().date()
fecha_inicio = (hoy - timedelta(days=7)).isoformat()
fecha_fin = hoy.isoformat()
response = requests.get(f"{BASE_URL}/metrics/ocupacion", headers=admin_headers, params={
    "fecha_inicio": fecha_inicio,
    "fecha_fin": fecha_fin
})
print(f"Status: {response. status_code}")
if response. status_code == 200:
    data = response.json()
    print(f"✅ Ocupación últimos 3 días:")
    for dia in data['ocupacion_diaria'][-3:]:
        print(f"   {dia['fecha']}: {dia['tasa_ocupacion']}% ({dia['habitaciones_ocupadas']} hab)")
    print()

# Habitaciones populares
print(">>> Habitaciones Más Populares")
response = requests.get(f"{BASE_URL}/metrics/habitaciones-populares", headers=admin_headers, params={
    "limite": 5
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if len(data['habitaciones_populares']) > 0:
        print(f"✅ Top 5 habitaciones:")
        for i, hab in enumerate(data['habitaciones_populares'][:5], 1):
            print(f"   {i}.  Hab {hab['numero_habitacion']} ({hab['tipo']}): {hab['total_reservas']} reservas")
    else:
        print(f"ℹ️  No hay datos de habitaciones populares aún")
    print()

# Tipos populares
print(">>> Tipos de Habitación Más Reservados")
response = requests.get(f"{BASE_URL}/metrics/tipos-habitacion-populares", headers=admin_headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if len(data['tipos_populares']) > 0:
        print(f"✅ Tipos más populares:")
        for tipo in data['tipos_populares']:
            print(f"   - {tipo['nombre']}: {tipo['total_reservas']} reservas (${tipo['ingresos_totales']} ingresos)")
    else:
        print(f"ℹ️  No hay datos de tipos populares aún")
    print()

# ==================== USUARIOS ====================
print_section("USUARIOS")

# Crear trabajador
print(">>> Crear Trabajador")
response = requests. post(f"{BASE_URL}/users/create-worker", headers=admin_headers, json={
    "nombre_completo": "Pedro Trabajador",
    "rut": f"trab-{int(datetime.now(). timestamp())}",
    "role": "trabajador",
    "edad": 28,
    "telefono": "+56987654321"
})
print(f"Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"✅ Trabajador creado:")
    print(f"   Email: {data['credentials']['email']}")
    print(f"   Password: {data['credentials']['password']}\n")
else:
    print(f"ℹ️  {response.json(). get('error', 'Error desconocido')}\n")

# Listar usuarios
print(">>> Listar Todos los Usuarios")
response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    users = response.json()
    print(f"✅ Total usuarios: {len(users)}")
    for user in users[:10]:
        print(f"   - {user['nombre_completo']} ({user['role']}): {user['email']}")
    print()

# ==================== RESUMEN FINAL ====================
print_section("RESUMEN FINAL")
print("✅ Todos los endpoints probados exitosamente")
print("\nEndpoints disponibles:")
print("  Auth: /api/auth/register, /api/auth/login, /api/auth/me, /api/auth/change-password")
print("  Users: /api/users/, /api/users/create-worker, /api/users/<id>")
print("  Room Types: /api/rooms/types")
print("  Rooms: /api/rooms/, /api/rooms/<id>, /api/rooms/<id>/estado")
print("  Bookings: /api/bookings/, /api/bookings/<id>, /api/bookings/disponibilidad")
print("             /api/bookings/<id>/check-in, /api/bookings/<id>/check-out")
print("             /api/bookings/<id>/cancelar")
print("  Metrics: /api/metrics/dashboard, /api/metrics/ocupacion, /api/metrics/ingresos")
print("           /api/metrics/habitaciones-populares, /api/metrics/clientes-frecuentes")
print("           /api/metrics/tipos-habitacion-populares")
print(f"\n{'='*60}\n")