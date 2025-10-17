"""
Script para verificar la conexión a la base de datos y variables de entorno
"""
import os
import sys
from dotenv import load_dotenv

# ✅ Cargar el archivo .env
load_dotenv()

print("=" * 60)
print("VERIFICANDO CONFIGURACIÓN DE BASE DE DATOS")
print("=" * 60)

# Verificar variables de entorno
print("\n📋 Variables de entorno:")
print(f"DB_HOST: {os.environ.get('DB_HOST', '❌ NO CONFIGURADO')}")
print(f"DB_USER: {os.environ.get('DB_USER', '❌ NO CONFIGURADO')}")
print(f"DB_PASSWORD: {'***' if os.environ.get('DB_PASSWORD') else '❌ NO CONFIGURADO'}")
print(f"DB_NAME: {os.environ.get('DB_NAME', '❌ NO CONFIGURADO')}")
print(f"DB_PORT: {os.environ.get('DB_PORT', '3306 (default)')}")

# Verificar si hay archivo .env
env_file = os.path.join(os.path.dirname(__file__), '.env')
print(f"\n📄 Archivo .env: {'✅ Existe' if os.path.exists(env_file) else '❌ No existe'}")

if os.path.exists(env_file):
    print("\nContenido de .env:")
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                # Ocultar valores sensibles
                if '=' in line:
                    key, _ = line.split('=', 1)
                    if 'PASSWORD' in key.upper() or 'SECRET' in key.upper():
                        print(f"  {key.strip()}=***")
                    else:
                        print(f"  {line.strip()}")

# Si no hay variables de entorno, no intentar conectar
if not os.environ.get('DB_HOST'):
    print("\n" + "=" * 60)
    print("⚠️  NO SE DETECTARON VARIABLES DE ENTORNO")
    print("=" * 60)
    print("\nOpciones:")
    print("1. Crear archivo .env con las credenciales de la base de datos")
    print("2. Configurar variables de entorno del sistema")
    print("3. Si quieres conectarte a la BD de Render, necesitas:")
    print("   - Obtener las credenciales de Render Dashboard")
    print("   - Crear archivo .env con esas credenciales")
    print("\nEjemplo de archivo .env:")
    print("""
DB_HOST=tu-host.oregon-postgres.render.com
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=nombre_base_datos
DB_PORT=3306
SECRET_KEY=tu_clave_secreta
""")
    sys.exit(1)

# Intentar conexión
print("\n" + "=" * 60)
print("🔌 INTENTANDO CONECTAR A LA BASE DE DATOS")
print("=" * 60)

try:
    import mysql.connector
    
    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME'),
        port=int(os.environ.get('DB_PORT', '3306')),
        connect_timeout=10
    )
    
    print("✅ CONEXIÓN EXITOSA")
    
    # Probar consulta simple
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM producto WHERE is_active = 1")
    total_productos = cursor.fetchone()[0]
    print(f"✅ Total de productos activos: {total_productos}")
    
    cursor.execute("SELECT COUNT(DISTINCT departamento) FROM producto WHERE is_active = 1")
    total_departamentos = cursor.fetchone()[0]
    print(f"✅ Total de departamentos: {total_departamentos}")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 La base de datos está funcionando correctamente")
    
except Exception as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")
    print("\n💡 Posibles soluciones:")
    print("1. Verificar que las credenciales en .env sean correctas")
    print("2. Verificar que la base de datos esté accesible (firewall, red)")
    print("3. Si es Render, verificar que la BD esté activa")
    print("4. Verificar que el puerto sea correcto (3306 para MySQL)")
    sys.exit(1)
