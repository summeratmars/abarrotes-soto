"""
Script de prueba para verificar que la API funciona correctamente
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8001"

def print_result(test_name, success, message=""):
    """Imprimir resultado de prueba"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")
    print()

def test_health():
    """Probar endpoint de health check"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            success = data.get('status') == 'healthy' and data.get('database') == 'connected'
            print_result("Health Check", success, f"Status: {data}")
            return success
        else:
            print_result("Health Check", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result("Health Check", False, f"Error: {str(e)}")
        return False

def test_productos():
    """Probar endpoint de productos"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/productos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            productos = data.get('productos', [])
            print_result("Obtener Productos", True, f"Se obtuvieron {len(productos)} productos")
            if productos:
                print(f"   Ejemplo: {productos[0].get('nombre_producto', 'N/A')}")
            print()
            return True
        else:
            print_result("Obtener Productos", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result("Obtener Productos", False, f"Error: {str(e)}")
        return False

def test_departamentos():
    """Probar endpoint de departamentos"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/departamentos", timeout=5)
        if response.status_code == 200:
            data = response.json()
            departamentos = data.get('departamentos', [])
            print_result("Obtener Departamentos", True, f"Encontrados: {', '.join(departamentos[:5])}")
            return True
        else:
            print_result("Obtener Departamentos", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result("Obtener Departamentos", False, f"Error: {str(e)}")
        return False

def test_categorias():
    """Probar endpoint de categorías"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/categorias", timeout=5)
        if response.status_code == 200:
            data = response.json()
            categorias = data.get('categorias', [])
            print_result("Obtener Categorías", True, f"{len(categorias)} categorías encontradas")
            return True
        else:
            print_result("Obtener Categorías", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result("Obtener Categorías", False, f"Error: {str(e)}")
        return False

def test_count():
    """Probar endpoint de conteo"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/productos/count", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print_result("Contar Productos", True, f"Total: {total} productos")
            return True
        else:
            print_result("Contar Productos", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result("Contar Productos", False, f"Error: {str(e)}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("=" * 60)
    print("  PRUEBAS DE API - ABARROTES SOTO")
    print("=" * 60)
    print(f"URL Base: {API_BASE_URL}")
    print()
    
    # Verificar que la API esté disponible
    try:
        response = requests.get(API_BASE_URL, timeout=5)
        if response.status_code != 200:
            print("❌ Error: La API no está respondiendo correctamente")
            print(f"   Asegúrate de que está corriendo en {API_BASE_URL}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar a la API")
        print(f"   Asegúrate de ejecutar: python db_api_server.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
    
    print("✅ API está respondiendo")
    print()
    print("-" * 60)
    print()
    
    # Ejecutar pruebas
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Productos", test_productos()))
    results.append(("Departamentos", test_departamentos()))
    results.append(("Categorías", test_categorias()))
    results.append(("Conteo", test_count()))
    
    # Resumen
    print("=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Pruebas exitosas: {passed}/{total}")
    print()
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
        print()
        print("La API está lista para usarse. Puedes:")
        print("  1. Ver la documentación en: http://localhost:8000/docs")
        print("  2. Configurar tu app en Render con la variable API_BASE_URL")
        print("  3. Exponer la API con ngrok o port forwarding")
    else:
        print("⚠️  Algunas pruebas fallaron")
        print("   Revisa los errores arriba y verifica:")
        print("   - Las credenciales en .env")
        print("   - La conexión a MySQL")
        print("   - Los logs de la API")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
