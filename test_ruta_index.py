#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la ruta index con parámetros de departamento y categoría
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar la app Flask
from app import app

def probar_ruta():
    """Prueba la ruta index con diferentes parámetros"""
    print("="*60)
    print("PROBANDO RUTA INDEX CON PARÁMETROS")
    print("="*60)
    
    with app.test_client() as client:
        # Prueba 1: Sin parámetros
        print("\n1️⃣ SIN PARÁMETROS:")
        response = client.get('/')
        print(f"   Status: {response.status_code}")
        if b'producto' in response.data or b'PRODUCTO' in response.data:
            print("   ✅ La página contiene la palabra 'producto'")
        else:
            print("   ❌ La página NO contiene productos")
        
        # Prueba 2: Con departamento
        print("\n2️⃣ CON DEPARTAMENTO 'ABARROTES Y DESPENSA':")
        response = client.get('/?departamento=ABARROTES Y DESPENSA')
        print(f"   Status: {response.status_code}")
        
        # Buscar si hay productos en la respuesta
        contenido = response.data.decode('utf-8', errors='ignore')
        
        if 'No hay productos disponibles' in contenido:
            print("   ❌ Mensaje: 'No hay productos disponibles'")
        elif 'productos_data' in contenido or 'producto-item' in contenido:
            print("   ✅ Se encontraron productos en la respuesta")
            # Contar productos
            count = contenido.count('producto-item')
            print(f"   📦 Aproximadamente {count} productos encontrados")
        else:
            print("   ⚠️  No se pudo determinar si hay productos")
        
        # Prueba 3: Con categoría
        print("\n3️⃣ CON CATEGORÍA 'CHILES SECOS':")
        response = client.get('/?categoria=CHILES SECOS')
        print(f"   Status: {response.status_code}")
        
        contenido = response.data.decode('utf-8', errors='ignore')
        
        if 'No hay productos disponibles' in contenido:
            print("   ❌ Mensaje: 'No hay productos disponibles'")
        elif 'productos_data' in contenido or 'producto-item' in contenido:
            print("   ✅ Se encontraron productos en la respuesta")
            count = contenido.count('producto-item')
            print(f"   📦 Aproximadamente {count} productos encontrados")
        else:
            print("   ⚠️  No se pudo determinar si hay productos")
        
        # Prueba 4: Con departamento desde la URL de las capturas
        print("\n4️⃣ CON DEPARTAMENTO 'ABARROTES%20Y%20DESPENSA' (URL encoded):")
        response = client.get('/?departamento=ABARROTES%20Y%20DESPENSA&categoria=CHILES%20SECOS')
        print(f"   Status: {response.status_code}")
        
        contenido = response.data.decode('utf-8', errors='ignore')
        
        if 'No hay productos disponibles' in contenido:
            print("   ❌ Mensaje: 'No hay productos disponibles'")
        elif 'productos_data' in contenido or 'producto-item' in contenido:
            print("   ✅ Se encontraron productos en la respuesta")
            count = contenido.count('producto-item')
            print(f"   📦 Aproximadamente {count} productos encontrados")
        else:
            print("   ⚠️  No se pudo determinar si hay productos")

if __name__ == '__main__':
    try:
        probar_ruta()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
