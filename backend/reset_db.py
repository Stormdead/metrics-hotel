"""
Script para resetear la base de datos de prueba
⚠️  CUIDADO: Esto eliminará TODOS los datos
"""
import mysql.connector
from getpass import getpass

print("="*60)
print("  ⚠️  RESETEAR BASE DE DATOS")
print("="*60)
print("\n⚠️  ADVERTENCIA: Esto eliminará TODOS los datos\n")

confirmar = input("¿Estás seguro?  Escribe 'SI' para continuar: ")

if confirmar != "SI":
    print("\n❌ Operación cancelada")
    exit()

# Conectar a MySQL
password = getpass("Password de MySQL: ")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="manuelrivas",
        password=password
    )
    cursor = conn. cursor()
    
    print("\n>>> Eliminando base de datos...")
    cursor.execute("DROP DATABASE IF EXISTS metrics_hotel")
    
    print(">>> Creando base de datos...")
    cursor.execute("CREATE DATABASE metrics_hotel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    
    cursor.close()
    conn.close()
    
    print("✅ Base de datos reseteada\n")
    print("Ahora ejecuta:")
    print("  flask db upgrade")
    print("  flask create-admin")
    print("  python test_complete.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")