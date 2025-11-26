"""
Script para listar las bases de datos disponibles en MariaDB
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print("🔍 Conectando a MariaDB para listar bases de datos...")
    
    # Conectar sin especificar base de datos
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    
    print("✅ Conectado exitosamente")
    print("\n📋 Bases de datos disponibles:")
    print("-" * 50)
    
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    
    databases = cursor.fetchall()
    for db in databases:
        print(f"   • {db[0]}")
    
    cursor.close()
    conn.close()
    
    print("-" * 50)
    print("\n💡 Copia el nombre exacto de tu base de datos")
    
except Exception as e:
    print(f"❌ Error: {e}")
