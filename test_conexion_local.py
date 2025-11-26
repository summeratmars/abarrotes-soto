"""
Script para probar la conexión a la base de datos local MariaDB
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def probar_conexion():
    try:
        print("🔍 Probando conexión a MariaDB local...")
        print(f"   Host: {os.getenv('DB_HOST')}")
        print(f"   Puerto: {os.getenv('DB_PORT')}")
        print(f"   Usuario: {os.getenv('DB_USER')}")
        print(f"   Base de datos: {os.getenv('DB_NAME')}")
        print()
        
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        print("✅ Conexión exitosa a MariaDB local")
        
        # Probar algunas consultas
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM producto')
        productos = cursor.fetchone()[0]
        print(f"✅ Total de productos: {productos}")
        
        cursor.execute('SELECT COUNT(*) FROM cliente')
        clientes = cursor.fetchone()[0]
        print(f"✅ Total de clientes: {clientes}")
        
        cursor.execute('SELECT DISTINCT nombre_dep FROM departamento LIMIT 5')
        departamentos = cursor.fetchall()
        print(f"✅ Departamentos encontrados: {len(departamentos)}")
        for dep in departamentos:
            print(f"   - {dep[0]}")
        
        cursor.close()
        conn.close()
        
        print()
        print("🎉 ¡La base de datos local está funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos:")
        print(f"   {str(e)}")
        return False

if __name__ == "__main__":
    probar_conexion()
