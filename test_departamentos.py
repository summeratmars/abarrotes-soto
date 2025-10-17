#!/usr/bin/env python3
"""Script para verificar departamentos y categorías en la base de datos"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

from db_utils import get_db_connection, obtener_productos_sucursal

def verificar_departamentos():
    """Verificar qué departamentos existen en la BD"""
    print("=" * 60)
    print("VERIFICANDO DEPARTAMENTOS Y CATEGORÍAS EN LA BASE DE DATOS")
    print("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Obtener departamentos
    print("\n📦 DEPARTAMENTOS DISPONIBLES:")
    cursor.execute("""
        SELECT DISTINCT d.nombre_dep, COUNT(p.uuid_producto) as total_productos
        FROM departamento d
        LEFT JOIN producto p ON d.uuid_departamento = p.uuid_departamento
        LEFT JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto
        WHERE ps.uuid_sucursal = '22C8131D-4431-4E9A-AA04-ED188217C549'
          AND ps.existencia >= 1
          AND p.is_active = 1
          AND ps.is_active = 1
        GROUP BY d.nombre_dep
        ORDER BY d.nombre_dep
    """)
    departamentos = cursor.fetchall()
    
    if departamentos:
        for i, dept in enumerate(departamentos, 1):
            print(f"{i}. {dept['nombre_dep']} ({dept['total_productos']} productos)")
    else:
        print("❌ No se encontraron departamentos")
    
    # Obtener categorías por departamento
    print("\n📂 CATEGORÍAS POR DEPARTAMENTO:")
    for dept in departamentos:
        nombre_dept = dept['nombre_dep']
        cursor.execute("""
            SELECT DISTINCT c.nombre_categoria, COUNT(p.uuid_producto) as total_productos
            FROM categoria c
            LEFT JOIN producto p ON c.uuid_categoria = p.uuid_categoria
            LEFT JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto
            LEFT JOIN departamento d ON p.uuid_departamento = d.uuid_departamento
            WHERE d.nombre_dep = %s
              AND ps.uuid_sucursal = '22C8131D-4431-4E9A-AA04-ED188217C549'
              AND ps.existencia >= 1
              AND p.is_active = 1
              AND ps.is_active = 1
            GROUP BY c.nombre_categoria
            ORDER BY c.nombre_categoria
        """, (nombre_dept,))
        categorias = cursor.fetchall()
        
        print(f"\n  {nombre_dept}:")
        if categorias:
            for cat in categorias:
                print(f"    • {cat['nombre_categoria']} ({cat['total_productos']} productos)")
        else:
            print(f"    ❌ Sin categorías")
    
    # Probar búsqueda con función
    print("\n" + "=" * 60)
    print("PROBANDO FUNCIÓN obtener_productos_sucursal()")
    print("=" * 60)
    
    # Probar cada departamento
    for dept in departamentos:
        nombre_dept = dept['nombre_dep']
        print(f"\n🔍 Buscando productos en: '{nombre_dept}'")
        productos = obtener_productos_sucursal(departamento=nombre_dept)
        print(f"   Resultado: {len(productos)} productos encontrados")
        
        if len(productos) == 0:
            # Debug: probar con consulta directa
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM producto p
                JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto
                LEFT JOIN departamento d ON p.uuid_departamento = d.uuid_departamento
                WHERE d.nombre_dep = %s
                  AND ps.uuid_sucursal = '22C8131D-4431-4E9A-AA04-ED188217C549'
                  AND ps.existencia >= 1
                  AND p.is_active = 1
                  AND ps.is_active = 1
            """, (nombre_dept,))
            resultado = cursor.fetchone()
            print(f"   ⚠️ Consulta directa encontró: {resultado['total']} productos")
    
    # Probar categorías
    print("\n🔍 PROBANDO CATEGORÍA 'CHILES SECOS':")
    productos = obtener_productos_sucursal(categoria='CHILES SECOS')
    print(f"   Resultado: {len(productos)} productos encontrados")
    
    cursor.execute("""
        SELECT c.nombre_categoria, COUNT(*) as total
        FROM producto p
        JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto
        LEFT JOIN categoria c ON p.uuid_categoria = c.uuid_categoria
        WHERE c.nombre_categoria = 'CHILES SECOS'
          AND ps.uuid_sucursal = '22C8131D-4431-4E9A-AA04-ED188217C549'
          AND ps.existencia >= 1
          AND p.is_active = 1
          AND ps.is_active = 1
        GROUP BY c.nombre_categoria
    """)
    resultado = cursor.fetchone()
    if resultado:
        print(f"   Consulta directa encontró: {resultado['total']} productos")
    else:
        print(f"   ❌ No existe la categoría 'CHILES SECOS'")
    
    # Mostrar categorías exactas que existen
    print("\n📋 CATEGORÍAS EXACTAS EN LA BD:")
    cursor.execute("""
        SELECT DISTINCT c.nombre_categoria
        FROM categoria c
        ORDER BY c.nombre_categoria
    """)
    todas_categorias = cursor.fetchall()
    for cat in todas_categorias:
        print(f"   • '{cat['nombre_categoria']}'")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    try:
        verificar_departamentos()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
