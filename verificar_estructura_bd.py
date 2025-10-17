#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para verificar la estructura exacta de las tablas."""

import os
from dotenv import load_dotenv
from db_utils import get_db_connection

# Cargar variables de entorno
load_dotenv()

def verificar_estructura():
    """Verifica la estructura de las tablas departamento, categoria y producto."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("=" * 60)
    print("VERIFICANDO ESTRUCTURA DE TABLAS")
    print("=" * 60)
    
    # Verificar estructura de tabla departamento
    print("\n📋 ESTRUCTURA DE TABLA 'departamento':")
    cursor.execute("DESCRIBE departamento")
    columns_dept = cursor.fetchall()
    for col in columns_dept:
        print(f"  • {col['Field']} ({col['Type']})")
    
    # Verificar estructura de tabla categoria
    print("\n📋 ESTRUCTURA DE TABLA 'categoria':")
    cursor.execute("DESCRIBE categoria")
    columns_cat = cursor.fetchall()
    for col in columns_cat:
        print(f"  • {col['Field']} ({col['Type']})")
    
    # Verificar estructura de tabla producto
    print("\n📋 ESTRUCTURA DE TABLA 'producto' (primeras 15 columnas):")
    cursor.execute("DESCRIBE producto")
    columns_prod = cursor.fetchall()
    for col in columns_prod[:15]:
        print(f"  • {col['Field']} ({col['Type']})")
    
    # Hacer un query de ejemplo con los datos reales
    print("\n" + "=" * 60)
    print("QUERY DE EJEMPLO CON DATOS REALES")
    print("=" * 60)
    
    cursor.execute('''
        SELECT 
            p.cbarras,
            p.nombre_producto,
            d.nombre_dep,
            c.nombre_categoria,
            ps.precio_venta,
            ps.existencia
        FROM producto p
        JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto
        LEFT JOIN departamento d ON p.uuid_departamento = d.uuid_departamento
        LEFT JOIN categoria c ON p.uuid_categoria = c.uuid_categoria
        WHERE ps.uuid_sucursal = '22C8131D-4431-4E9A-AA04-ED188217C549'
          AND ps.existencia >= 1
          AND p.is_active = 1
          AND ps.is_active = 1
        LIMIT 5
    ''')
    
    productos = cursor.fetchall()
    print(f"\n✅ Se encontraron {len(productos)} productos de ejemplo:")
    for i, prod in enumerate(productos, 1):
        print(f"\n{i}. {prod['nombre_producto']}")
        print(f"   Código: {prod['cbarras']}")
        print(f"   Departamento: {prod['nombre_dep']}")
        print(f"   Categoría: {prod['nombre_categoria']}")
        print(f"   Precio: ${prod['precio_venta']}")
        print(f"   Existencia: {prod['existencia']}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    verificar_estructura()
