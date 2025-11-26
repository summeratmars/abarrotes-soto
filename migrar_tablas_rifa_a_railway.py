"""
Script para exportar tablas de RIFA desde la BD local
y luego importarlas a Railway
"""
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Cargar variables de entorno
load_dotenv()

def obtener_estructura_tabla(cursor, tabla):
    """Obtiene el CREATE TABLE de una tabla"""
    cursor.execute(f"SHOW CREATE TABLE {tabla}")
    result = cursor.fetchone()
    if result:
        create_statement = result[1]
        # Reemplazar collations incompatibles
        create_statement = create_statement.replace('utf8mb4_ucai400_ai_ci', 'utf8mb4_unicode_ci')
        create_statement = create_statement.replace('utf8mb4_0900_ai_ci', 'utf8mb4_unicode_ci')
        create_statement = create_statement.replace('utf8mb3_general_ci', 'utf8mb4_unicode_ci')
        # Asegurar que use InnoDB
        if 'ENGINE=' not in create_statement:
            create_statement = create_statement.rstrip(';') + ' ENGINE=InnoDB'
        return create_statement
    return None

def exportar_datos_tabla(cursor, tabla):
    """Exporta los datos de una tabla como INSERT statements"""
    cursor.execute(f"SELECT * FROM {tabla}")
    rows = cursor.fetchall()
    
    if not rows:
        return []
    
    # Obtener nombres de columnas
    cursor.execute(f"DESCRIBE {tabla}")
    columnas = [col[0] for col in cursor.fetchall()]
    
    inserts = []
    for row in rows:
        valores = []
        for valor in row:
            if valor is None:
                valores.append('NULL')
            elif isinstance(valor, (int, float)):
                valores.append(str(valor))
            elif isinstance(valor, str):
                # Escapar comillas simples
                valor_escapado = valor.replace("'", "\\'").replace('"', '\\"')
                valores.append(f"'{valor_escapado}'")
            else:
                valores.append(f"'{str(valor)}'")
        
        insert = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({', '.join(valores)});"
        inserts.append(insert)
    
    return inserts

def exportar_tablas_rifa():
    """Exporta las tablas de rifa desde la BD local"""
    print("=" * 80)
    print("📤 EXPORTAR TABLAS DE RIFA DESDE BASE DE DATOS LOCAL")
    print("=" * 80)
    
    tablas_rifa = ['rifa', 'rifa_boleto', 'rifa_ganadores']
    
    try:
        # Conectar a la base de datos LOCAL
        print("\n🔄 Conectando a base de datos local (MariaDB)...")
        print("   Host: localhost")
        print("   Puerto: 4407")
        print("   Base de datos: puntoventa_db")
        
        conn_local = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='puntoventa_db',
            port=4407
        )
        
        if conn_local.is_connected():
            print("✅ Conectado a MariaDB local")
            cursor_local = conn_local.cursor()
            
            # Crear archivo SQL de exportación
            archivo_export = 'export_tablas_rifa.sql'
            
            with open(archivo_export, 'w', encoding='utf-8') as f:
                f.write("-- ================================================\n")
                f.write("-- EXPORTACIÓN DE TABLAS DE RIFA\n")
                f.write("-- Desde: puntoventa_db (LOCAL)\n")
                f.write("-- Para: railway (PRODUCCIÓN)\n")
                f.write("-- Fecha: 2025-11-05\n")
                f.write("-- ================================================\n\n")
                f.write("USE railway;\n\n")
                f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
                
                for tabla in tablas_rifa:
                    print(f"\n📋 Procesando tabla: {tabla}")
                    
                    # Verificar si la tabla existe
                    cursor_local.execute(f"SHOW TABLES LIKE '{tabla}'")
                    if not cursor_local.fetchone():
                        print(f"   ⚠️  Tabla {tabla} no encontrada, saltando...")
                        continue
                    
                    # Obtener estructura
                    print(f"   → Obteniendo estructura...")
                    estructura = obtener_estructura_tabla(cursor_local, tabla)
                    
                    if estructura:
                        # Modificar DROP TABLE para que sea condicional
                        f.write(f"-- ================================================\n")
                        f.write(f"-- TABLA: {tabla}\n")
                        f.write(f"-- ================================================\n")
                        f.write(f"DROP TABLE IF EXISTS `{tabla}`;\n\n")
                        
                        # Limpiar el CREATE TABLE de collations incompatibles
                        estructura_limpia = estructura.replace('utf8mb4_uca1400_ai_ci', 'utf8mb4_unicode_ci')
                        estructura_limpia = estructura_limpia.replace('utf8mb4_ucai400_ai_ci', 'utf8mb4_unicode_ci')
                        estructura_limpia = estructura_limpia.replace('utf8mb4_0900_ai_ci', 'utf8mb4_unicode_ci')
                        estructura_limpia = estructura_limpia.replace('utf8mb3_general_ci', 'utf8mb4_unicode_ci')
                        estructura_limpia = estructura_limpia.replace('utf8_general_ci', 'utf8mb4_unicode_ci')
                        
                        f.write(estructura_limpia + ";\n\n")
                        
                        # Obtener datos
                        print(f"   → Obteniendo datos...")
                        cursor_local.execute(f"SELECT COUNT(*) FROM {tabla}")
                        count = cursor_local.fetchone()[0]
                        print(f"   → {count} registros encontrados")
                        
                        if count > 0:
                            inserts = exportar_datos_tabla(cursor_local, tabla)
                            f.write(f"-- Datos de {tabla} ({len(inserts)} registros)\n")
                            for insert in inserts:
                                f.write(insert + "\n")
                            f.write("\n")
                        
                        print(f"   ✅ Tabla {tabla} exportada")
                    else:
                        print(f"   ❌ No se pudo obtener estructura de {tabla}")
                
                f.write("\nSET FOREIGN_KEY_CHECKS=1;\n")
                f.write("\n-- ================================================\n")
                f.write("-- FIN DE LA EXPORTACIÓN\n")
                f.write("-- ================================================\n")
            
            cursor_local.close()
            print(f"\n✅ Exportación completada!")
            print(f"📄 Archivo generado: {archivo_export}")
            
            return archivo_export
            
    except Error as e:
        print(f"\n❌ ERROR AL EXPORTAR:")
        print(f"   {str(e)}")
        return None
        
    finally:
        if 'conn_local' in locals() and conn_local.is_connected():
            conn_local.close()
            print("🔌 Conexión local cerrada")

def importar_a_railway(archivo_sql):
    """Importa el archivo SQL a Railway"""
    print("\n" + "=" * 80)
    print("📥 IMPORTAR TABLAS DE RIFA A RAILWAY")
    print("=" * 80)
    
    if not os.path.exists(archivo_sql):
        print(f"\n❌ Error: No se encontró el archivo '{archivo_sql}'")
        return False
    
    try:
        # Leer el archivo SQL
        print(f"\n📄 Leyendo archivo: {archivo_sql}")
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
            print(f"✅ Conectado a Railway")
            
            cursor = connection.cursor()
            
            # Dividir el script en statements
            # Primero separar CREATE TABLE de INSERT
            create_statements = []
            insert_rifa = []  # INSERT de tabla rifa primero
            insert_boletos = []  # INSERT de boletos después
            insert_ganadores = []  # INSERT de ganadores al final
            other_statements = []
            
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            for stmt in statements:
                stmt_clean = stmt.strip()
                if not stmt_clean or stmt_clean.startswith('--'):
                    continue
                
                if 'CREATE TABLE' in stmt_clean.upper() or 'DROP TABLE' in stmt_clean.upper():
                    create_statements.append(stmt_clean)
                elif stmt_clean.upper().startswith('INSERT INTO'):
                    # Separar inserts por tabla para controlar el orden
                    if 'INSERT INTO rifa_boleto' in stmt_clean or 'INSERT INTO `rifa_boleto`' in stmt_clean:
                        insert_boletos.append(stmt_clean)
                    elif 'INSERT INTO rifa_ganadores' in stmt_clean or 'INSERT INTO `rifa_ganadores`' in stmt_clean:
                        insert_ganadores.append(stmt_clean)
                    elif 'INSERT INTO rifa' in stmt_clean or 'INSERT INTO `rifa`' in stmt_clean:
                        insert_rifa.append(stmt_clean)
                elif stmt_clean.upper() in ['USE RAILWAY', 'SET FOREIGN_KEY_CHECKS=0', 'SET FOREIGN_KEY_CHECKS=1']:
                    other_statements.append(stmt_clean)
            
            # Combinar inserts en el orden correcto
            insert_statements = insert_rifa + insert_boletos + insert_ganadores
            
            total = len(create_statements) + len(insert_statements) + len(other_statements)
            print(f"\n📊 Total statements: {total}")
            print(f"   • CREATE/DROP: {len(create_statements)}")
            print(f"   • INSERT: {len(insert_statements)}")
            print(f"   • OTHER: {len(other_statements)}\n")
            
            contador = 0
            
            # 1. Ejecutar statements de configuración
            print("🔧 Paso 1: Configuración...")
            for stmt in other_statements:
                try:
                    cursor.execute(stmt)
                    contador += 1
                except Error as e:
                    if "Unknown database" not in str(e):
                        print(f"   ⚠️  {str(e)[:80]}")
            
            # 2. Ejecutar CREATE/DROP TABLE
            print(f"📋 Paso 2: Creando tablas...")
            for i, stmt in enumerate(create_statements, 1):
                try:
                    cursor.execute(stmt)
                    contador += 1
                    if 'CREATE TABLE' in stmt.upper():
                        # Extraer nombre de tabla
                        tabla_match = stmt.split('CREATE TABLE')[1].split('(')[0].strip()
                        print(f"   ✓ Tabla creada: {tabla_match}")
                except Error as e:
                    print(f"   ⚠️  {str(e)[:80]}")
            
            connection.commit()
            print(f"✅ Tablas creadas correctamente")
            
            # 3. Ejecutar INSERT
            print(f"\n📥 Paso 3: Insertando datos...")
            print(f"   • Rifa: {len(insert_rifa)} registros")
            print(f"   • Boletos: {len(insert_boletos)} registros")
            print(f"   • Ganadores: {len(insert_ganadores)} registros")
            
            # Deshabilitar foreign key checks temporalmente
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            except:
                pass
            errores = 0
            for i, stmt in enumerate(insert_statements, 1):
                try:
                    cursor.execute(stmt)
                    contador += 1
                    if i % 20 == 0:
                        print(f"   ✓ {i}/{len(insert_statements)} registros insertados...")
                except Error as e:
                    if "Duplicate entry" not in str(e):
                        errores += 1
                        if errores <= 3:  # Solo mostrar primeros 3 errores
                            print(f"   ⚠️  Error {errores}: {str(e)[:100]}")
            
            if errores > 3:
                print(f"   ⚠️  ... y {errores - 3} errores más")
            
            print(f"   ✓ {len(insert_statements) - errores}/{len(insert_statements)} registros insertados correctamente")
            
            # Rehabilitar foreign key checks
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            except:
                pass
            
            connection.commit()
            print(f"\n✅ Importación completada!")
            
            # Verificar tablas
            print(f"\n📊 Verificando tablas en Railway...")
            cursor.execute("SHOW TABLES LIKE 'rifa%'")
            tablas = cursor.fetchall()
            
            if tablas:
                print(f"\n✅ Tablas de rifa en Railway:")
                for tabla in tablas:
                    nombre_tabla = tabla[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
                    count = cursor.fetchone()[0]
                    print(f"   • {nombre_tabla}: {count} registros")
            
            cursor.close()
            return True
            
    except Error as e:
        print(f"\n❌ ERROR AL IMPORTAR A RAILWAY:")
        print(f"   {str(e)}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print(f"\n🔌 Conexión a Railway cerrada")

if __name__ == "__main__":
    print("\n🎯 MIGRACIÓN DE TABLAS DE RIFA: LOCAL → RAILWAY\n")
    
    # Paso 1: Exportar desde local
    archivo_export = exportar_tablas_rifa()
    
    if archivo_export:
        # Paso 2: Importar a Railway
        exito = importar_a_railway(archivo_export)
        
        if exito:
            print("\n" + "=" * 80)
            print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
            print("=" * 80)
            print("\n✅ Las tablas de rifa ahora están disponibles en Railway")
            print("✅ Tu sistema de punto de venta puede acceder a ellas\n")
        else:
            print("\n❌ Hubo problemas en la importación a Railway")
    else:
        print("\n❌ No se pudo completar la exportación desde la BD local")
