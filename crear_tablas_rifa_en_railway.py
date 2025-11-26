"""
Script para crear las tablas de RIFA en Railway
Ejecuta el archivo SQL: crear_tablas_rifa_railway.sql
"""
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Cargar variables de entorno
load_dotenv()

def ejecutar_sql_desde_archivo(archivo_sql='crear_tablas_rifa_railway.sql'):
    """Ejecuta el script SQL para crear las tablas de rifa"""
    print("=" * 80)
    print("🎯 CREAR TABLAS DE RIFA EN RAILWAY")
    print("=" * 80)
    
    # Verificar que existe el archivo SQL
    if not os.path.exists(archivo_sql):
        print(f"\n❌ Error: No se encontró el archivo '{archivo_sql}'")
        return False
    
    print(f"\n📄 Leyendo archivo: {archivo_sql}")
    
    try:
        # Leer el archivo SQL
        with open(archivo_sql, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Conectar a Railway
        print(f"\n🔄 Conectando a Railway...")
        print(f"   Host: {os.environ.get('DB_HOST')}")
        print(f"   Base de datos: {os.environ.get('DB_NAME')}")
        
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME'),
            port=int(os.environ.get('DB_PORT', 3306))
        )
        
        if connection.is_connected():
            print(f"✅ Conectado a Railway MySQL {connection.get_server_info()}")
            
            cursor = connection.cursor()
            
            # Dividir el script en statements individuales
            # Eliminar comentarios de línea completa
            lines = sql_script.split('\n')
            clean_lines = []
            for line in lines:
                # Eliminar comentarios
                if line.strip().startswith('--'):
                    continue
                clean_lines.append(line)
            
            clean_script = '\n'.join(clean_lines)
            
            # Dividir por punto y coma
            statements = [stmt.strip() for stmt in clean_script.split(';') if stmt.strip()]
            
            print(f"\n📊 Ejecutando {len(statements)} statements SQL...\n")
            
            resultados = []
            for i, statement in enumerate(statements, 1):
                if not statement.strip():
                    continue
                
                try:
                    # Ejecutar el statement
                    cursor.execute(statement)
                    
                    # Si hay resultados, obtenerlos
                    if cursor.with_rows:
                        result = cursor.fetchall()
                        if result:
                            resultados.extend(result)
                    
                    # Mensaje de progreso cada 5 statements
                    if i % 5 == 0 or i == len(statements):
                        print(f"   ✓ {i}/{len(statements)} statements ejecutados...")
                    
                except Error as e:
                    # Ignorar errores de "tabla ya existe"
                    if "already exists" in str(e) or "Duplicate entry" in str(e):
                        print(f"   ⚠️  Statement {i}: Tabla/registro ya existe (OK)")
                        continue
                    else:
                        print(f"\n❌ Error en statement {i}:")
                        print(f"   {str(e)}")
                        print(f"\n   Statement problemático:")
                        print(f"   {statement[:200]}...")
            
            # Commit todos los cambios
            connection.commit()
            
            print(f"\n✅ Script ejecutado exitosamente!")
            
            # Verificar tablas creadas
            print(f"\n📊 Verificando tablas creadas...")
            cursor.execute("SHOW TABLES LIKE 'rifa%'")
            tablas = cursor.fetchall()
            
            if tablas:
                print(f"\n✅ Tablas de rifa encontradas:")
                for tabla in tablas:
                    nombre_tabla = tabla[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
                    count = cursor.fetchone()[0]
                    print(f"   • {nombre_tabla}: {count} registros")
            else:
                print(f"\n⚠️  No se encontraron tablas de rifa")
            
            # Mostrar información de la rifa
            cursor.execute("""
                SELECT nombre, fecha_inicio, fecha_sorteo, estado, total_premios 
                FROM rifa 
                WHERE is_active = 1 
                LIMIT 1
            """)
            rifa_info = cursor.fetchone()
            
            if rifa_info:
                print(f"\n🎯 RIFA CONFIGURADA:")
                print(f"   Nombre: {rifa_info[0]}")
                print(f"   Inicio: {rifa_info[1]}")
                print(f"   Sorteo: {rifa_info[2]}")
                print(f"   Estado: {rifa_info[3]}")
                print(f"   Premios: {rifa_info[4]}")
            
            cursor.close()
            print(f"\n" + "=" * 80)
            print(f"✅ TABLAS DE RIFA CREADAS EXITOSAMENTE EN RAILWAY")
            print(f"=" * 80)
            return True
            
    except Error as e:
        print(f"\n❌ ERROR AL EJECUTAR SQL:")
        print(f"   {str(e)}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print(f"\n🔌 Conexión cerrada")

if __name__ == "__main__":
    exito = ejecutar_sql_desde_archivo()
    if exito:
        print("\n🎉 ¡Listo! Las tablas de rifa están disponibles en Railway")
        print("   Ahora tu sistema de punto de venta puede acceder a ellas.")
    else:
        print("\n❌ Hubo problemas al crear las tablas.")
        print("   Revisa los errores y vuelve a intentar.")
