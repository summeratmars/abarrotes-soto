import json
import uuid
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import re
import os

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'puntoventa_db'),
        port=int(os.environ.get('DB_PORT', '3306'))
    )

def guardar_cotizacion_web(carrito, observaciones='Generado por tienda en línea'):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(CAST(folio AS UNSIGNED)) FROM cotizacion WHERE folio REGEXP ''^[0-9]+db_utils.py''')
        last = cursor.fetchone()
        if last and last[0]:
            folio_num = int(last[0]) + 1
        else:
            folio_num = 12
        folio = str(folio_num)

        uuid_cotizacion = str(uuid.uuid4())
        uuid_cliente = '00000000-0000-0000-0000-000000000000'
        uuid_sucursal = '22C8131D-4431-4E9A-AA04-ED188217C549'

        productos = []
        subtotal = 0.0
        descuento_total = 0.0
        
        for prod in carrito:
            cantidad = float(prod.get('cantidad', 1))
            codigo_barras = prod.get('cbarras', '')
            
            cursor.execute(''SELECT p.cbarras, p.nombre_producto, ps.precio_venta, ps.precio_venta2, ps.dCantMinPP2, u.clave_unidad FROM producto p JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto LEFT JOIN c_unidad u ON p.clave_unidad = u.clave_unidad WHERE p.cbarras = %s AND ps.uuid_sucursal = %s'', (codigo_barras, uuid_sucursal))
            producto_info = cursor.fetchone()
            
            if producto_info:
                precio_venta = float(producto_info[2])
                precio_venta2 = float(producto_info[3]) if producto_info[3] else 0.0
                dcantminpp2 = float(producto_info[4]) if producto_info[4] else 0.0
                unidad = producto_info[5] or 'PZA'
                nombre = producto_info[1]
                
                precio_aplicable = precio_venta
                if precio_venta2 > 0 and dcantminpp2 > 0 and cantidad >= dcantminpp2:
                    precio_aplicable = precio_venta2
                
                subtotal_prod = cantidad * precio_aplicable
                importe_original = cantidad * precio_venta
                
                productos.append({
                    'codigo_barras': codigo_barras,
                    'nombre': nombre,
                    'cantidad': cantidad,
                    'precio_unitario': precio_aplicable,
                    'subtotal': subtotal_prod,
                    'importe_original': importe_original,
                    'unidad': unidad
                })
                
                subtotal += importe_original
                descuento_total += (importe_original - subtotal_prod)
            else:
                precio = float(prod.get('precio', 0))
                subtotal_prod = cantidad * precio
                productos.append({
                    'codigo_barras': codigo_barras,
                    'nombre': prod.get('nombre', ''),
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'subtotal': subtotal_prod,
                    'importe_original': subtotal_prod,
                    'unidad': 'PZA'
                })
                subtotal += subtotal_prod

        total = subtotal - descuento_total

        hoy = datetime.now()
        fecha_vencimiento = (hoy + timedelta(days=30)).strftime('%Y-%m-%d')
        creado_en = hoy.strftime('%Y-%m-%d %H:%M:%S')

        cot_json = {
            'uuid_cotizacion': uuid_cotizacion,
            'cliente_id': None,
            'productos': productos,
            'subtotal': subtotal,
            'descuento': descuento_total,
            'total': total,
            'forma_pago': None,
            'metodo_pago': None,
            'condiciones': 'Pedido en línea',
            'observaciones': observaciones,
            'fecha_vencimiento': fecha_vencimiento,
            'creado_en': creado_en
        }

        sql = 'INSERT INTO cotizacion (folio, json, fecha_vencimiento, subtotal, descuento, total, uuid_cliente, uuid_sucursal, uuid_cotizacion, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (folio, json.dumps(cot_json, ensure_ascii=False), fecha_vencimiento, subtotal, descuento_total, total, uuid_cliente, uuid_sucursal, uuid_cotizacion, 1))
        conn.commit()
        return folio, uuid_cotizacion
    except Exception as e:
        conn.rollback()
        print(f'Error al guardar cotización: {e}')
        return None, None
    finally:
        conn.close()

def obtener_productos_sucursal(sucursal_uuid='22C8131D-4431-4E9A-AA04-ED188217C549', departamento=None, categoria=None, query=None, orden=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = 'SELECT p.cbarras, p.nombre_producto, ps.precio_venta, ps.precio_venta2, ps.dCantMinPP2, ps.existencia, p.puntos_lealtad, d.nombre_dep AS nombre_departamento, c.nombre_categoria, u.nombre_unidad FROM producto p JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto LEFT JOIN departamento d ON p.uuid_departamento = d.uuid_departamento LEFT JOIN categoria c ON p.uuid_categoria = c.uuid_categoria LEFT JOIN c_unidad u ON p.clave_unidad = u.clave_unidad WHERE ps.uuid_sucursal = %s AND ps.existencia >= 1 AND p.is_active = 1 AND ps.is_active = 1'
    params = [sucursal_uuid]
    if departamento:
        sql += ' AND d.nombre_dep = %s'
        params.append(departamento)
    if categoria:
        sql += ' AND c.nombre_categoria = %s'
        params.append(categoria)
    if query:
        sql += ' AND (LOWER(p.nombre_producto) LIKE %s OR LOWER(c.nombre_categoria) LIKE %s OR LOWER(d.nombre_dep) LIKE %s)'
        palabra = f'%{query.strip().lower()}%'
        params.extend([palabra, palabra, palabra])
    if orden == 'nombre_asc':
        sql += ' ORDER BY p.nombre_producto ASC'
    elif orden == 'precio_asc':
        sql += ' ORDER BY COALESCE(NULLIF(ps.precio_venta2,0), ps.precio_venta) ASC'
    elif orden == 'precio_desc':
        sql += ' ORDER BY COALESCE(NULLIF(ps.precio_venta2,0), ps.precio_venta) DESC'
    
    cursor.execute(sql, params)
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos

def registrar_cliente_monedero(nombre_completo, telefono, sucursal_uuid='22C8131D-4431-4E9A-AA04-ED188217C549'):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT idcliente FROM cliente WHERE telefono = %s AND is_active=1 LIMIT 1', (telefono,))
        if cursor.fetchone():
            return None, 'El teléfono ya está registrado.'

        partes = re.split(r'\s+', nombre_completo.strip())
        if len(partes) == 1:
            nombre = partes[0]
            apellidos = ''
        elif len(partes) == 2:
            nombre = partes[0]
            apellidos = partes[1]
        else:
            nombre = partes[0]
            apellidos = ' '.join(partes[1:])

        sql_cliente = 'INSERT INTO cliente (nombre, apellidos, telefono, uuid_sucursal, is_active) VALUES (%s, %s, %s, %s, 1)'
        cursor.execute(sql_cliente, (nombre, apellidos, telefono, sucursal_uuid))
        idcliente = cursor.lastrowid

        vCodigoCliente = f'CLI{idcliente:05d}'
        cursor.execute('UPDATE cliente SET vCodigoCliente = %s WHERE idcliente = %s', (vCodigoCliente, idcliente))
        conn.commit()
        return {
            'idcliente': idcliente,
            'vCodigoCliente': vCodigoCliente,
            'nombre': nombre,
            'apellidos': apellidos
        }, None
    except Exception as e:
        conn.rollback()
        return None, f'Error al registrar: {e}'
    finally:
        conn.close()

def obtener_cliente_por_telefono(telefono):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT idcliente, vCodigoCliente, nombre, apellidos, puntos_lealtad, telefono FROM cliente WHERE telefono = %s AND is_active = 1 LIMIT 1', (telefono,))
        return cursor.fetchone()
    except Exception as e:
        print(f'Error al obtener cliente: {e}')
        return None
    finally:
        conn.close()
