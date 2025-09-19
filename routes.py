from flask import Blueprint, request, render_template, jsonify, redirect, url_for, flash, session
import json
import re
from db_utils import obtener_productos_sucursal, guardar_cotizacion_web, registrar_cliente_monedero, obtener_cliente_por_telefono

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def index():
    departamentos = ['Abarrotes', 'Bebidas', 'Dulces y Snacks', 'Lácteos', 'Carnes y Embutidos', 'Limpieza', 'Cuidado Personal']
    return render_template('index.html', departamentos=departamentos)

@main_routes.route('/api/productos')
def api_productos():
    departamento = request.args.get('departamento')
    categoria = request.args.get('categoria')
    query = request.args.get('q', '')
    orden = request.args.get('orden', '')
    
    productos = obtener_productos_sucursal(
        departamento=departamento,
        categoria=categoria,
        query=query.strip() if query else None,
        orden=orden if orden else None
    )
    
    # Formatear productos para la respuesta JSON
    productos_formateados = []
    for prod in productos:
        precio_final = prod['precio_venta']
        precio_oferta = None
        
        if prod['precio_venta2'] and prod['precio_venta2'] > 0 and prod['dCantMinPP2'] and prod['dCantMinPP2'] > 0:
            precio_oferta = {
                'precio': prod['precio_venta2'],
                'cantidad_minima': prod['dCantMinPP2']
            }
        
        productos_formateados.append({
            'cbarras': prod['cbarras'],
            'nombre_producto': prod['nombre_producto'],
            'precio_venta': precio_final,
            'precio_oferta': precio_oferta,
            'existencia': prod['existencia'],
            'puntos_lealtad': prod['puntos_lealtad'] or 0,
            'nombre_departamento': prod['nombre_departamento'],
            'nombre_categoria': prod['nombre_categoria'],
            'nombre_unidad': prod['nombre_unidad'] or 'PZA'
        })
    
    return jsonify(productos_formateados)

@main_routes.route('/cart')
def cart():
    return render_template('cart.html')

@main_routes.route('/checkout')
def checkout():
    return render_template('checkout.html')

@main_routes.route('/api/cotizar', methods=['POST'])
def api_cotizar():
    try:
        data = request.get_json()
        if not data or 'productos' not in data:
            return jsonify({'success': False, 'error': 'Datos inválidos'}), 400
        
        carrito = data['productos']
        observaciones = data.get('observaciones', 'Generado por tienda en línea')
        
        if not carrito:
            return jsonify({'success': False, 'error': 'El carrito está vacío'}), 400
        
        folio, uuid_cot = guardar_cotizacion_web(carrito, observaciones)
        
        if folio:
            return jsonify({
                'success': True,
                'folio': folio,
                'uuid_cotizacion': uuid_cot,
                'mensaje': f'Cotización #{folio} creada exitosamente'
            })
        else:
            return jsonify({'success': False, 'error': 'Error al generar cotización'}), 500
            
    except Exception as e:
        print(f'Error en api_cotizar: {e}')
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@main_routes.route('/confirmacion')
def confirmacion():
    folio = request.args.get('folio', 'N/A')
    return render_template('confirmacion.html', folio=folio)

@main_routes.route('/monedero')
def monedero():
    return render_template('monedero.html')

@main_routes.route('/api/registrar-cliente', methods=['POST'])
def api_registrar_cliente():
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()
        telefono = data.get('telefono', '').strip()
        
        if not nombre or not telefono:
            return jsonify({'success': False, 'error': 'Nombre y teléfono son requeridos'}), 400
        
        # Validar formato de teléfono (10 dígitos)
        if not re.match(r'^\d{10}$', telefono):
            return jsonify({'success': False, 'error': 'El teléfono debe tener 10 dígitos'}), 400
        
        cliente_info, error = registrar_cliente_monedero(nombre, telefono)
        
        if cliente_info:
            return jsonify({
                'success': True,
                'cliente': cliente_info,
                'mensaje': f'Cliente {cliente_info["vCodigoCliente"]} registrado exitosamente'
            })
        else:
            return jsonify({'success': False, 'error': error}), 400
            
    except Exception as e:
        print(f'Error en api_registrar_cliente: {e}')
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@main_routes.route('/api/buscar-cliente', methods=['POST'])
def api_buscar_cliente():
    try:
        data = request.get_json()
        telefono = data.get('telefono', '').strip()
        
        if not telefono:
            return jsonify({'success': False, 'error': 'Teléfono es requerido'}), 400
        
        if not re.match(r'^\d{10}$', telefono):
            return jsonify({'success': False, 'error': 'El teléfono debe tener 10 dígitos'}), 400
        
        cliente = obtener_cliente_por_telefono(telefono)
        
        if cliente:
            return jsonify({
                'success': True,
                'cliente': {
                    'idcliente': cliente['idcliente'],
                    'vCodigoCliente': cliente['vCodigoCliente'],
                    'nombre_completo': f"{cliente['nombre']} {cliente['apellidos']}".strip(),
                    'puntos_lealtad': cliente['puntos_lealtad'] or 0,
                    'telefono': cliente['telefono']
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
            
    except Exception as e:
        print(f'Error en api_buscar_cliente: {e}')
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500
