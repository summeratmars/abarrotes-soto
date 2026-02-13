"""
Cliente para consumir la API REST local de Abarrotes Soto
Reemplaza las funciones de db_utils.py para trabajar con la API
en lugar de conectarse directamente a MySQL.
"""

import requests
import os
import threading
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Importar el notificador de imágenes para verificar productos sin imagen
try:
    from notificador_imagenes import verificar_imagen_producto
except ImportError:
    verificar_imagen_producto = None
    print("⚠️ notificador_imagenes no disponible")

# URL base de la API - debe apuntar a tu PC donde corre la API
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8001')

# Caché simple para productos (reduce llamadas a la API)
_cache_productos = {}
_cache_timeout = 300  # 5 minutos en segundos
_cache_timestamps = {}

def _verificar_imagenes_async(productos: List[Dict]):
    """
    Verifica imágenes de productos en un hilo separado para no bloquear la respuesta
    """
    if not verificar_imagen_producto:
        return
    
    for producto in productos:
        codigo_barras = producto.get('cbarras', '')
        nombre_producto = producto.get('nombre_producto', '')
        if codigo_barras:
            try:
                verificar_imagen_producto(codigo_barras, nombre_producto)
            except Exception as e:
                print(f"⚠️ Error verificando imagen de {codigo_barras}: {e}")

class APIConnectionError(Exception):
    """Excepción personalizada para errores de conexión a la API"""
    pass

def _make_request(method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
    """
    Función auxiliar para realizar peticiones HTTP a la API
    """
    url = f"{API_BASE_URL}{endpoint}"
    # Header necesario para evitar la página de advertencia de ngrok free
    headers = kwargs.pop('headers', {})
    headers['ngrok-skip-browser-warning'] = 'true'
    try:
        response = requests.request(method, url, timeout=30, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise APIConnectionError("Tiempo de espera agotado al conectar con la API")
    except requests.exceptions.ConnectionError:
        raise APIConnectionError(f"No se pudo conectar con la API en {API_BASE_URL}")
    except requests.exceptions.HTTPError as e:
        error_detail = "Error desconocido"
        try:
            error_detail = response.json().get('detail', str(e))
        except:
            error_detail = str(e)
        raise APIConnectionError(f"Error HTTP: {error_detail}")
    except Exception as e:
        raise APIConnectionError(f"Error inesperado: {str(e)}")

def get_db_connection():
    """
    Mantener compatibilidad con código existente.
    Nota: Con la API no necesitamos conexiones directas,
    pero mantenemos esta función para no romper el código existente.
    """
    # Esta función ya no hace nada real, solo verifica que la API esté disponible
    try:
        response = _make_request('GET', '/health')
        if response.get('status') != 'healthy':
            raise APIConnectionError("La API no está saludable")
        return True
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo verificar la API: {e}")
        return None

def obtener_productos_sucursal(
    sucursal_uuid=None,  # ignorado en nueva BD
    departamento: Optional[str] = None,
    categoria: Optional[str] = None,
    query: Optional[str] = None,
    orden: Optional[str] = None,
    pagina: int = 1,
    por_pagina: Optional[int] = None
) -> List[Dict]:
    """
    Obtiene productos de la sucursal mediante la API REST
    Incluye caché para mejorar rendimiento
    """
    import time
    
    # Crear clave de caché basada en los parámetros
    cache_key = f"{sucursal_uuid}_{departamento}_{categoria}_{query}_{orden}_{pagina}_{por_pagina}"
    
    # Verificar si hay datos en caché y si son válidos
    current_time = time.time()
    if cache_key in _cache_productos:
        cached_time = _cache_timestamps.get(cache_key, 0)
        if current_time - cached_time < _cache_timeout:
            print(f"📦 Usando caché para productos (key: {cache_key[:30]}...)")
            return _cache_productos[cache_key]
    
    params = {
        'pagina': pagina
    }
    
    if departamento:
        params['departamento'] = departamento
    if categoria:
        params['categoria'] = categoria
    if query:
        params['query'] = query
    if orden:
        params['orden'] = orden
    if por_pagina:
        params['por_pagina'] = por_pagina
    
    try:
        response = _make_request('GET', '/api/productos', params=params)
        productos = response.get('productos', [])
        
        # Guardar en caché
        _cache_productos[cache_key] = productos
        _cache_timestamps[cache_key] = current_time
        
        # Limpiar caché viejo (máximo 50 entradas)
        if len(_cache_productos) > 50:
            oldest_key = min(_cache_timestamps, key=_cache_timestamps.get)
            del _cache_productos[oldest_key]
            del _cache_timestamps[oldest_key]
        
        # Verificar imágenes de productos en segundo plano (no bloquea la respuesta)
        if verificar_imagen_producto and productos:
            thread = threading.Thread(
                target=_verificar_imagenes_async, 
                args=(productos,),
                daemon=True
            )
            thread.start()
        
        return productos
    except APIConnectionError as e:
        print(f"❌ Error al obtener productos: {e}")
        return []

def contar_productos_sucursal(
    sucursal_uuid=None,  # ignorado en nueva BD
    departamento: Optional[str] = None,
    categoria: Optional[str] = None,
    query: Optional[str] = None
) -> int:
    """
    Cuenta productos según filtros mediante la API REST
    """
    params = {}
    
    if departamento:
        params['departamento'] = departamento
    if categoria:
        params['categoria'] = categoria
    if query:
        params['query'] = query
    
    try:
        response = _make_request('GET', '/api/productos/count', params=params)
        return response.get('total', 0)
    except APIConnectionError as e:
        print(f"❌ Error al contar productos: {e}")
        return 0

def guardar_cotizacion_web(carrito: List[Dict], observaciones: str = "Generado por tienda en línea"):
    """
    Guarda una cotización web mediante la API REST
    """
    try:
        payload = {
            'carrito': carrito,
            'observaciones': observaciones
        }
        response = _make_request('POST', '/api/cotizacion', json=payload)
        return response.get('folio'), response.get('uuid_cotizacion')
    except APIConnectionError as e:
        print(f"❌ Error al guardar cotización: {e}")
        return None, None

def registrar_cliente_monedero(
    nombre_completo: str,
    telefono: str,
    sucursal_uuid: str = None  # ignorado en nueva BD
):
    """
    Registra un cliente en el sistema de monedero mediante la API REST
    """
    try:
        payload = {
            'nombre_completo': nombre_completo,
            'telefono': telefono
        }
        response = _make_request('POST', '/api/cliente/monedero', json=payload)
        return response, None
    except APIConnectionError as e:
        return None, str(e)

def consultar_puntos_cliente(busqueda: str):
    """
    Consulta los puntos de un cliente mediante la API REST
    """
    try:
        response = _make_request('GET', '/api/cliente/puntos', params={'busqueda': busqueda})
        return response, None
    except APIConnectionError as e:
        return None, str(e)

def guardar_pedido_db(
    nombre: str,
    direccion: str,
    colonia: str,
    telefono: str,
    numero_cliente: str,
    pago: str,
    carrito: List[Dict]
):
    """
    Guarda un pedido y sus detalles mediante la API REST
    """
    try:
        payload = {
            'nombre': nombre,
            'direccion': direccion,
            'colonia': colonia,
            'telefono': telefono,
            'numero_cliente': numero_cliente or "",
            'pago': pago,
            'carrito': carrito
        }
        response = _make_request('POST', '/api/pedido', json=payload)
        return response.get('pedido_id')
    except APIConnectionError as e:
        print(f"❌ Error al guardar pedido: {e}")
        return None

def obtener_departamentos() -> List[str]:
    """
    Obtiene la lista de departamentos únicos
    """
    try:
        response = _make_request('GET', '/api/departamentos')
        return response.get('departamentos', [])
    except APIConnectionError as e:
        print(f"❌ Error al obtener departamentos: {e}")
        return []

def obtener_categorias(departamento: Optional[str] = None) -> List[str]:
    """
    Obtiene la lista de categorías, opcionalmente filtradas por departamento
    """
    params = {}
    if departamento:
        params['departamento'] = departamento
    
    try:
        response = _make_request('GET', '/api/categorias', params=params)
        return response.get('categorias', [])
    except APIConnectionError as e:
        print(f"❌ Error al obtener categorías: {e}")
        return []


# ---------------------------------------------------------------------------
# FUNCIONES ADMIN (via API REST)
# ---------------------------------------------------------------------------
def obtener_producto_por_codigo(codigo_barras: str) -> Optional[Dict]:
    """Obtiene un producto completo por código de barras via API"""
    try:
        response = _make_request('GET', f'/api/admin/producto/{codigo_barras}')
        return response
    except APIConnectionError as e:
        print(f"❌ Error al obtener producto: {e}")
        return None


def obtener_todos_productos_admin(pagina: int = 1, por_pagina: int = 50):
    """Obtiene productos paginados para el panel admin via API"""
    try:
        response = _make_request('GET', '/api/admin/productos', params={
            'pagina': pagina, 'por_pagina': por_pagina
        })
        return response.get('productos', []), response.get('total', 0)
    except APIConnectionError as e:
        print(f"❌ Error al obtener productos admin: {e}")
        return [], 0


def crear_producto_db(datos: Dict):
    """Crea un nuevo producto via API"""
    try:
        payload = {
            'cbarras': datos.get('cbarras', ''),
            'nombre_producto': datos.get('nombre_producto', ''),
            'precio_venta': float(datos.get('precio_venta', 0)),
            'existencia': float(datos.get('existencia', 0)),
            'nombre_categoria': datos.get('nombre_categoria'),
            'nombre_dep': datos.get('nombre_dep'),
            'unidad_medida': datos.get('unidad_medida', 'PZA'),
            'precio_venta2': float(datos.get('precio_venta2', 0)),
            'imagen': datos.get('imagen')
        }
        response = _make_request('POST', '/api/admin/producto', json=payload)
        return response.get('producto_id'), None
    except APIConnectionError as e:
        return None, str(e)


def actualizar_producto_db(codigo_barras: str, datos: Dict):
    """Actualiza un producto existente via API"""
    try:
        payload = {
            'cbarras': datos.get('cbarras', codigo_barras),
            'nombre_producto': datos.get('nombre_producto', ''),
            'precio_venta': float(datos.get('precio_venta', 0)),
            'existencia': float(datos.get('existencia', 0)),
            'nombre_categoria': datos.get('nombre_categoria'),
            'nombre_dep': datos.get('nombre_dep'),
            'unidad_medida': datos.get('unidad_medida', 'PZA'),
            'precio_venta2': float(datos.get('precio_venta2', 0)),
            'imagen': datos.get('imagen')
        }
        response = _make_request('PUT', f'/api/admin/producto/{codigo_barras}', json=payload)
        return response.get('success', False), None
    except APIConnectionError as e:
        return False, str(e)


def eliminar_producto_db(codigo_barras: str) -> bool:
    """Desactiva un producto via API"""
    try:
        response = _make_request('DELETE', f'/api/admin/producto/{codigo_barras}')
        return response.get('success', False)
    except APIConnectionError as e:
        print(f"❌ Error al eliminar producto: {e}")
        return False


def obtener_productos_bajo_stock(limite: int = 5) -> List[Dict]:
    """Obtiene productos con stock bajo via API"""
    try:
        response = _make_request('GET', '/api/admin/productos/bajo-stock', params={'limite': limite})
        return response.get('productos', [])
    except APIConnectionError as e:
        print(f"❌ Error al obtener productos bajo stock: {e}")
        return []


def obtener_estadisticas_admin() -> Dict:
    """Obtiene estadísticas para el dashboard admin via API"""
    try:
        response = _make_request('GET', '/api/admin/estadisticas')
        return response
    except APIConnectionError as e:
        print(f"❌ Error al obtener estadísticas: {e}")
        return {
            'total_productos': 0, 'total_clientes': 0,
            'pedidos_pendientes': 0, 'ventas_mes': 0,
            'ultimos_pedidos': []
        }


def obtener_pedidos_admin() -> List[Dict]:
    """Obtiene todos los pedidos online para admin via API"""
    try:
        response = _make_request('GET', '/api/admin/pedidos')
        return response.get('pedidos', [])
    except APIConnectionError as e:
        print(f"❌ Error al obtener pedidos: {e}")
        return []


def actualizar_estado_pedido(pedido_id, nuevo_estado: str) -> bool:
    """Actualiza el estado de un pedido via API"""
    try:
        response = _make_request('PUT', f'/api/admin/pedido/{pedido_id}/estado',
                                  json={'nuevo_estado': nuevo_estado})
        return response.get('success', False)
    except APIConnectionError as e:
        print(f"❌ Error al actualizar estado: {e}")
        return False
