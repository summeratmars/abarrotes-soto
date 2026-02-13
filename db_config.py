"""
Módulo auxiliar para detectar automáticamente el entorno
y cargar el módulo DB correcto (API o directo)
"""

import os
import sys

def usar_api_rest():
    """
    Detecta si la app debe usar la API REST o conexión directa
    Returns: True si debe usar API, False si debe usar conexión directa
    """
    # Detectar si estamos en un entorno de producción cloud
    es_render = os.environ.get('RENDER') is not None
    es_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    es_heroku = os.environ.get('DYNO') is not None
    
    # Si se especifica explícitamente usar la API
    force_api = os.environ.get('USE_API', '').lower() in ('true', '1', 'yes')
    
    return es_render or es_railway or es_heroku or force_api

def get_db_module():
    """
    Importa y retorna el módulo de base de datos correcto
    """
    if usar_api_rest():
        print("🌐 [DB CONFIG] Modo: Producción - Usando API REST")
        try:
            import db_api_client as db_module
            api_url = os.environ.get('API_BASE_URL', 'No configurada')
            print(f"🔗 [DB CONFIG] API URL: {api_url}")
            return db_module
        except ImportError as e:
            print(f"❌ [DB CONFIG] Error al importar db_api_client: {e}")
            print("⚠️  [DB CONFIG] Fallback a conexión directa")
            import db_utils as db_module
            return db_module
    else:
        print("💻 [DB CONFIG] Modo: Local - Conexión directa a MySQL")
        import db_utils as db_module
        return db_module

# Obtener el módulo correcto
db = get_db_module()

# Exportar las funciones necesarias
get_db_connection = db.get_db_connection
obtener_productos_sucursal = db.obtener_productos_sucursal
guardar_pedido_db = db.guardar_pedido_db
contar_productos_sucursal = db.contar_productos_sucursal
guardar_cotizacion_web = db.guardar_cotizacion_web
registrar_cliente_monedero = db.registrar_cliente_monedero

# Agregar funciones de departamentos y categorías
try:
    obtener_departamentos = db.obtener_departamentos
    obtener_categorias = db.obtener_categorias
    consultar_puntos_cliente = db.consultar_puntos_cliente
except AttributeError:
    # Si no existen en el módulo, crear funciones fallback
    def obtener_departamentos():
        return []
    def obtener_categorias(departamento=None):
        return []
    def consultar_puntos_cliente(busqueda):
        return None, "Función no disponible"

# Funciones auxiliares de admin (nuevas para BD azula_pdv)
try:
    obtener_producto_por_codigo = db.obtener_producto_por_codigo
    obtener_todos_productos_admin = db.obtener_todos_productos_admin
    crear_producto_db = db.crear_producto_db
    actualizar_producto_db = db.actualizar_producto_db
    eliminar_producto_db = db.eliminar_producto_db
    obtener_productos_bajo_stock = db.obtener_productos_bajo_stock
    obtener_estadisticas_admin = db.obtener_estadisticas_admin
    obtener_pedidos_admin = db.obtener_pedidos_admin
    actualizar_estado_pedido = db.actualizar_estado_pedido
except AttributeError:
    pass

__all__ = [
    'get_db_connection',
    'obtener_productos_sucursal',
    'guardar_pedido_db',
    'contar_productos_sucursal',
    'guardar_cotizacion_web',
    'registrar_cliente_monedero',
    'obtener_departamentos',
    'obtener_categorias',
    'consultar_puntos_cliente',
    'usar_api_rest',
    'obtener_producto_por_codigo',
    'obtener_todos_productos_admin',
    'crear_producto_db',
    'actualizar_producto_db',
    'eliminar_producto_db',
    'obtener_productos_bajo_stock',
    'obtener_estadisticas_admin',
    'obtener_pedidos_admin',
    'actualizar_estado_pedido',
]
