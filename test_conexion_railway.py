"""
Script para probar la conexión a la base de datos de Railway
"""
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Cargar variables de entorno
load_dotenv()

def test_railway_connection():
    """Prueba la conexión a Railway MySQL"""
    print("=" * 70)
    print("🔍 PRUEBA DE CONEXIÓN A RAILWAY MYSQL")
    print("=" * 70)
    
    # Mostrar configuración (sin mostrar password completo)
    print("\n📋 Configuración actual:")
    print(f"   Host: {os.environ.get('DB_HOST')}")
    print(f"   Puerto: {os.environ.get('DB_PORT')}")
    print(f"   Base de datos: {os.environ.get('DB_NAME')}")
    print(f"   Usuario: {os.environ.get('DB_USER')}")
    password = os.environ.get('DB_PASSWORD', '')
    print(f"   Password: {'*' * (len(password) - 4)}{password[-4:] if len(password) >= 4 else '****'}")
    
    print("\n🔄 Intentando conectar...")
    
    try:
        # Intentar conexión
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME'),
            port=int(os.environ.get('DB_PORT', 3306))
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"\n✅ ¡CONEXIÓN EXITOSA!")
            print(f"   Versión MySQL: {db_info}")
            
            # Probar una consulta simple
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"   Base de datos actual: {db_name[0]}")
            
            # Contar tablas
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"   Número de tablas: {len(tables)}")
            
            if tables:
                print("\n📊 Tablas encontradas:")
                for table in tables[:10]:  # Mostrar solo las primeras 10
                    print(f"      - {table[0]}")
                if len(tables) > 10:
                    print(f"      ... y {len(tables) - 10} más")
            
            # Verificar algunas tablas importantes
            cursor.execute("SHOW TABLES LIKE 'producto';")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM producto WHERE is_active = 1;")
                count = cursor.fetchone()[0]
                print(f"\n✅ Tabla 'producto': {count} productos activos")
            
            cursor.execute("SHOW TABLES LIKE 'cliente';")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM cliente WHERE is_active = 1;")
                count = cursor.fetchone()[0]
                print(f"✅ Tabla 'cliente': {count} clientes activos")
            
            cursor.execute("SHOW TABLES LIKE 'cotizacion';")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM cotizacion WHERE is_active = 1;")
                count = cursor.fetchone()[0]
                print(f"✅ Tabla 'cotizacion': {count} cotizaciones activas")
            
            cursor.close()
            
    except Error as e:
        print(f"\n❌ ERROR AL CONECTAR:")
        print(f"   {str(e)}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que las credenciales en .env sean correctas")
        print("   2. Asegúrate que Railway esté activo y en ejecución")
        print("   3. Confirma que el puerto 18465 no esté bloqueado por firewall")
        print("   4. Verifica tu conexión a internet")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("\n🔌 Conexión cerrada correctamente")
    
    print("\n" + "=" * 70)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 70)
    return True

if __name__ == "__main__":
    test_railway_connection()
