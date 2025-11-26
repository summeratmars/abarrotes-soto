"""
Cliente para consumir la API REST local de Abarrotes Soto
Reemplaza las funciones de db_utils.py para trabajar con la API
en lugar de conectarse directamente a MySQL.
"""

import requests
import os
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

class APIConnectionError(Exception):
    """Excepción personalizada para errores de conexión a la API"""
    pass

def _make_request(method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
    """
    Función auxiliar para realizar peticiones HTTP a la API
    """
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, timeout=30, **kwargs)
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
    sucursal_uuid='22C8131D-4431-4E9A-AA04-ED188217C549',
    departamento: Optional[str] = None,
    categoria: Optional[str] = None,
    query: Optional[str] = None,
    orden: Optional[str] = None,
    pagina: int = 1,
    por_pagina: Optional[int] = None
) -> List[Dict]:
    """
    Obtiene productos de la sucursal mediante la API REST
    """
    params = {
        'sucursal_uuid': sucursal_uuid,
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
        
        # Verificar imágenes de productos y enviar notificaciones si es necesario
        if verificar_imagen_producto:
            for producto in productos:
                codigo_barras = producto.get('cbarras', '')
                nombre_producto = producto.get('nombre_producto', '')
                if codigo_barras:
                    # Verificar imagen del producto (envía notificación si no tiene)
                    verificar_imagen_producto(codigo_barras, nombre_producto)
        
        return productos
    except APIConnectionError as e:
        print(f"❌ Error al obtener productos: {e}")
        return []

def contar_productos_sucursal(
    sucursal_uuid='22C8131D-4431-4E9A-AA04-ED188217C549',
    departamento: Optional[str] = None,
    categoria: Optional[str] = None,
    query: Optional[str] = None
) -> int:
    """
    Cuenta productos según filtros mediante la API REST
    """
    params = {'sucursal_uuid': sucursal_uuid}
    
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
    sucursal_uuid: str = '22C8131D-4431-4E9A-AA04-ED188217C549'
):
    """
    Registra un cliente en el sistema de monedero mediante la API REST
    """
    try:
        payload = {
            'nombre_completo': nombre_completo,
            'telefono': telefono,
            'sucursal_uuid': sucursal_uuid
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
