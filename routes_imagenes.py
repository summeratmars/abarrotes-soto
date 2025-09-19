from flask import Blueprint, request, jsonify
from notificador_imagenes import (
    verificar_imagen_producto, 
    obtener_estadisticas_imagenes,
    limpiar_notificaciones_antiguas,
    cargar_productos_notificados
)
import os

imagenes_bp = Blueprint('imagenes', __name__)

@imagenes_bp.route('/api/imagenes/verificar', methods=['POST'])
def verificar_imagen_manual():
    """Verificar manualmente la imagen de un producto específico"""
    try:
        data = request.json
        codigo_barras = data.get('codigo_barras', '')
        nombre_producto = data.get('nombre_producto', '')
        
        if not codigo_barras:
            return jsonify({
                'success': False, 
                'error': 'Código de barras es requerido'
            }), 400
        
        tiene_imagen = verificar_imagen_producto(codigo_barras, nombre_producto)
        
        return jsonify({
            'success': True,
            'codigo_barras': codigo_barras,
            'tiene_imagen': tiene_imagen,
            'mensaje': f'Imagen {"encontrada" if tiene_imagen else "NO encontrada"}'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@imagenes_bp.route('/api/imagenes/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtener estadísticas de productos con y sin imagen"""
    try:
        stats = obtener_estadisticas_imagenes()
        return jsonify({
            'success': True,
            'estadisticas': stats
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@imagenes_bp.route('/api/imagenes/limpiar-notificaciones', methods=['POST'])
def limpiar_notificaciones():
    """Limpiar notificaciones antiguas manualmente"""
    try:
        limpiar_notificaciones_antiguas()
        return jsonify({
            'success': True,
            'mensaje': 'Notificaciones antiguas limpiadas correctamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@imagenes_bp.route('/api/imagenes/productos-notificados', methods=['GET'])
def listar_productos_notificados():
    """Listar todos los productos que han sido notificados"""
    try:
        notificados = cargar_productos_notificados()
        
        productos_lista = []
        for codigo, datos in notificados.items():
            productos_lista.append({
                'codigo_barras': codigo,
                'nombre': datos.get('nombre', ''),
                'fecha_notificacion': datos.get('fecha', ''),
                'notificado': datos.get('notificado', False)
            })
        
        return jsonify({
            'success': True,
            'total': len(productos_lista),
            'productos': productos_lista
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@imagenes_bp.route('/api/imagenes/verificar-lote', methods=['POST'])
def verificar_lote_productos():
    """Verificar imágenes de múltiples productos"""
    try:
        data = request.json
        productos = data.get('productos', [])
        
        if not productos:
            return jsonify({
                'success': False,
                'error': 'Lista de productos es requerida'
            }), 400
        
        resultados = []
        for producto in productos:
            codigo = producto.get('codigo_barras', '')
            nombre = producto.get('nombre_producto', '')
            
            if codigo:
                tiene_imagen = verificar_imagen_producto(codigo, nombre)
                resultados.append({
                    'codigo_barras': codigo,
                    'nombre_producto': nombre,
                    'tiene_imagen': tiene_imagen
                })
        
        return jsonify({
            'success': True,
            'total_verificados': len(resultados),
            'resultados': resultados
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500