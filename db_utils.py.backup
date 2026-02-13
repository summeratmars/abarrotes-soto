import json
import uuid
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import re
import os
from dotenv import load_dotenv
from notificador_imagenes import verificar_imagen_producto

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME'),
        port=int(os.environ.get('DB_PORT', '3306'))
    )

# --- GUARDAR COTIZACION WEB ---
def guardar_cotizacion_web(carrito, observaciones="Generado por tienda en línea"):
    """
    Guarda una cotización web en la tabla cotizacion con el formato JSON requerido.
    El uuid_cliente será nulo para público general.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Obtener próximo número de folio (autoincremental simple)
        cursor.execute("SELECT MAX(CAST(folio AS UNSIGNED)) FROM cotizacion WHERE folio REGEXP '^[0-9]+$'")
        last = cursor.fetchone()
        if last and last[0]:
            folio_num = int(last[0]) + 1
        else:
            folio_num = 12  # Comenzar desde 12 como indica el contexto
        folio = str(folio_num)

        # uuid_cotizacion y uuid_cliente
        uuid_cotizacion = str(uuid.uuid4())
        uuid_cliente = '00000000-0000-0000-0000-000000000000'  # UUID nulo para público general
        uuid_sucursal = '22C8131D-4431-4E9A-AA04-ED188217C549'

        # Calcular totales consultando info completa de BD
        productos = []
        subtotal = 0.0
        descuento_total = 0.0
        
        for prod in carrito:
            cantidad = float(prod.get('cantidad', 1))
            codigo_barras = prod.get('cbarras') or prod.get('codigo_barras') or prod.get('codigo') or ""
            
            # Consultar información completa del producto desde BD
            cursor.execute('''
                SELECT p.cbarras, p.nombre_producto, ps.precio_venta, ps.precio_venta2, 
                       ps.dCantMinPP2, u.clave_unidad, p.is_granel, ps.precio_venta3, ps.dCantMinPP3
                FROM producto p
                JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto
                LEFT JOIN c_unidad u ON p.clave_unidad = u.clave_unidad
                WHERE p.cbarras = %s AND ps.uuid_sucursal = %s
            ''', (codigo_barras, uuid_sucursal))
            
            producto_info = cursor.fetchone()
            
            if producto_info:
                precio_venta = float(producto_info[2])
                precio_venta2 = float(producto_info[3]) if producto_info[3] else 0.0
                dcantminpp2 = float(producto_info[4]) if producto_info[4] else 0.0
                unidad_correcta = producto_info[5] or "PZA"
                nombre_producto = producto_info[1]
                is_granel = producto_info[6] or 0
                precio_venta3 = float(producto_info[7]) if producto_info[7] else 0.0
                dcantminpp3 = float(producto_info[8]) if producto_info[8] else 0.0
                
                # Calcular precio aplicable y descuento
                precio_aplicable = precio_venta
                descuento_unitario = 0.0
                
                # Prioridad: Mayoreo (precio3) > Oferta (precio2) > Normal
                if precio_venta3 > 0 and dcantminpp3 > 0 and cantidad >= dcantminpp3:
                    # Aplica precio de mayoreo
                    descuento_unitario = precio_venta - precio_venta3
                    precio_aplicable = precio_venta3
                elif precio_venta2 > 0 and dcantminpp2 > 0 and cantidad >= dcantminpp2:
                    # Aplica precio de oferta por cantidad
                    descuento_unitario = precio_venta - precio_venta2
                    precio_aplicable = precio_venta2
                
                subtotal_prod = cantidad * precio_aplicable
                descuento_prod = cantidad * descuento_unitario
                importe_original = cantidad * precio_venta  # Precio original sin descuento
                
                productos.append({
                    "codigo_barras": codigo_barras,
                    "nombre": nombre_producto,
                    "cantidad": cantidad,
                    "precio_unitario": precio_aplicable,
                    "subtotal": subtotal_prod,
                    "importe_original": importe_original,
                    "unidad": unidad_correcta
                })
                
                subtotal += importe_original  # ✅ CORREGIDO: Sumar precio ORIGINAL para subtotal
                descuento_total += descuento_prod
            else:
                # Fallback si no encontramos el producto en BD
                precio = float(prod.get('precio', 0))
                subtotal_prod = cantidad * precio
                productos.append({
                    "codigo_barras": codigo_barras,
                    "nombre": prod.get('nombre') or prod.get('nombre_producto') or "",
                    "cantidad": cantidad,
                    "precio_unitario": precio,
                    "subtotal": subtotal_prod,
                    "importe_original": subtotal_prod,
                    "unidad": "PZA"
                })
                subtotal += subtotal_prod
        
        # ✅ CORREGIDO: Total = Subtotal - Descuentos
        total = subtotal - descuento_total

        # Fechas
        hoy = datetime.now()
        fecha_vencimiento = (hoy + timedelta(days=30)).strftime("%Y-%m-%d")
        creado_en = hoy.strftime("%Y-%m-%d %H:%M:%S")

        # JSON exacto según formato especificado
        cot_json = {
            "uuid_cotizacion": uuid_cotizacion,
            "cliente_id": None,
            "productos": productos,
            "subtotal": subtotal,
            "descuento": descuento_total,
            "total": total,
            "forma_pago": None,
            "metodo_pago": None,
            "condiciones": "Pedido en línea",
            "observaciones": observaciones,
            "fecha_vencimiento": fecha_vencimiento,
            "creado_en": creado_en
        }

        # Insertar en cotizacion con todos los campos necesarios
        sql = """
            INSERT INTO cotizacion (
                folio, json, fecha_vencimiento, subtotal, descuento, total,
                uuid_cliente, uuid_sucursal, uuid_cotizacion, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            folio,
            json.dumps(cot_json, ensure_ascii=False),
            fecha_vencimiento,
            subtotal,
            descuento_total,  # ✅ AGREGAR campo descuento
            total,
            uuid_cliente,
            uuid_sucursal,
            uuid_cotizacion,
            1  # is_active
        ))
        conn.commit()
        return folio, uuid_cotizacion
    except Exception as e:
        conn.rollback()
        print(f"Error al guardar cotización: {e}")
        return None, None
    finally:
        conn.close()

def registrar_cliente_monedero(nombre_completo, telefono, sucursal_uuid='22C8131D-4431-4E9A-AA04-ED188217C549'):
    """
    Registra un cliente nuevo para la sucursal ABARROTES SOTO CH.
    - Separa nombre y apellidos.
    - Valida que el teléfono no exista.
    - Inserta en la tabla cliente.
    - Genera vCodigoCliente (CLI + idcliente con ceros).
    - Retorna vCodigoCliente, idcliente, nombre, apellidos.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # Validar que el teléfono no exista
        cursor.execute("SELECT idcliente FROM cliente WHERE telefono = %s AND is_active=1 LIMIT 1", (telefono,))
        if cursor.fetchone():
            return None, "El teléfono ya está registrado."

        # Separar nombre y apellidos
        partes = re.split(r'\s+', nombre_completo.strip())
        if len(partes) == 1:
            nombre = partes[0]
            apellidos = ''
        elif len(partes) == 2:
            nombre, apellidos = partes
        else:
            nombre = partes[0]
            apellidos = ' '.join(partes[1:])

        # Generar uuid_cliente
        uuid_cliente = str(uuid.uuid4())
        # Insertar cliente (agregando uuid_cliente)
        sql = (
            "INSERT INTO cliente (uuid_cliente, nombre, apellidos, razon_social, telefono, puntos, is_active) "
            "VALUES (%s, %s, %s, %s, %s, 0, 1)"
        )
        razon_social = nombre_completo.strip()
        cursor.execute(sql, (uuid_cliente, nombre, apellidos, razon_social, telefono))
        idcliente = cursor.lastrowid

        # Generar vCodigoCliente
        vCodigoCliente = f"CLI{idcliente:05d}"
        cursor.execute("UPDATE cliente SET vCodigoCliente = %s WHERE idcliente = %s", (vCodigoCliente, idcliente))
        conn.commit()
        return {
            'idcliente': idcliente,
            'vCodigoCliente': vCodigoCliente,
            'nombre': nombre,
            'apellidos': apellidos
        }, None
    except Exception as e:
        conn.rollback()
        return None, f"Error al registrar: {e}"
    finally:
        conn.close()

# --- GUARDAR PEDIDO Y DETALLE EN LA BASE DE DATOS ---
def guardar_pedido_db(nombre, direccion, colonia, telefono, numero_cliente, pago, carrito):
    """
    Guarda el pedido y sus productos en la base de datos.
    - carrito: lista de dicts con los productos (de localStorage)
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Insertar cabecera del pedido
            sql_pedido = """
                INSERT INTO pedido (nombre, direccion, colonia, telefono, numero_cliente, pago)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_pedido, (nombre, direccion, colonia, telefono, numero_cliente, pago))
            pedido_id = cursor.lastrowid

            # Insertar productos del pedido con todos los campos requeridos
            for prod in carrito:
                sql_detalle = """
                    INSERT INTO pedido_detalle (
                        pedido_id, nombre_producto, cantidad, precio,
                        codigo_barras, uuid_producto, clave_unidad,
                        precio_venta, precio_venta2, dCantMinPP2,
                        uuid_departamento, existencia
                    )
                    SELECT 
                        %s, p.nombre_producto, %s, %s,
                        p.cbarras, p.uuid_producto, p.clave_unidad,
                        ps.precio_venta, ps.precio_venta2, ps.dCantMinPP2,
                        p.uuid_departamento, ps.existencia
                    FROM producto p
                    JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto
                    WHERE p.nombre_producto = %s 
                        AND ps.is_active = 1 
                        AND ps.existencia > 0
                    LIMIT 1;
                """
                cursor.execute(sql_detalle, (
                    pedido_id,
                    prod.get('cantidad'),
                    prod.get('precio'),
                    prod.get('nombre')
                ))
        conn.commit()
        return pedido_id
    except Exception as e:
        conn.rollback()
        print(f"Error al guardar pedido: {e}")
        return None
    finally:
        conn.close()

# Obtiene productos y precios de la sucursal ABARROTES SOTO CH
def obtener_productos_sucursal(
    sucursal_uuid='22C8131D-4431-4E9A-AA04-ED188217C549',
    departamento=None,
    categoria=None,
    query=None,
    orden=None,
    pagina=1,
    por_pagina=None
):
    # DEBUG: Ver qué parámetros llegan a la función
    print(f"🔍 DEBUG obtener_productos_sucursal():")
    print(f"   departamento: '{departamento}'")
    print(f"   categoria: '{categoria}'")
    print(f"   query: '{query}'")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = '''
        SELECT 
            p.cbarras,
            p.nombre_producto,
            ps.precio_venta,
            ps.precio_venta2,
            ps.dCantMinPP2,
            ps.precio_venta3,
            ps.dCantMinPP3,
            ps.existencia,
            p.puntos_lealtad,
            d.nombre_dep AS nombre_departamento,
            c.nombre_categoria,
            u.nombre_unidad
        FROM producto p
        JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto
        LEFT JOIN categoria c ON p.uuid_categoria = c.uuid_categoria
        LEFT JOIN departamento d ON c.uuid_departamento = d.uuid_departamento
        LEFT JOIN c_unidad u ON p.clave_unidad = u.clave_unidad
        WHERE ps.uuid_sucursal = %s
          AND ps.existencia >= 1
          AND p.is_active = 1
          AND ps.is_active = 1
    '''
    params = [sucursal_uuid]
    if departamento:
        sql += ' AND d.nombre_dep = %s'
        params.append(departamento)
    if categoria:
        # Lógica especial para mostrar productos con descuento cuando categoria=ofertas
        if categoria.lower() == 'ofertas':
            sql += ' AND ps.precio_venta2 > 0 AND ps.precio_venta2 < ps.precio_venta'
        else:
            sql += ' AND c.nombre_categoria = %s'
            params.append(categoria)
    if query:
        sql += ' AND (LOWER(p.nombre_producto) LIKE %s OR LOWER(c.nombre_categoria) LIKE %s OR LOWER(d.nombre_dep) LIKE %s)'
        palabra = f"%{query.strip().lower()}%"
        params.extend([palabra, palabra, palabra])
    if orden == 'nombre_asc':
        sql += ' ORDER BY p.nombre_producto ASC'
    elif orden == 'precio_asc':
        sql += ' ORDER BY COALESCE(NULLIF(ps.precio_venta2,0), ps.precio_venta) ASC'
    elif orden == 'precio_desc':
        sql += ' ORDER BY COALESCE(NULLIF(ps.precio_venta2,0), ps.precio_venta) DESC'
    
    # Agregar paginación si se especifica
    if por_pagina:
        offset = (pagina - 1) * por_pagina
        sql += f' LIMIT {por_pagina} OFFSET {offset}'
    
    cursor.execute(sql, params)
    productos = cursor.fetchall()
    
    # Verificar imágenes de productos y enviar notificaciones si es necesario
    for producto in productos:
        codigo_barras = producto['cbarras'] if 'cbarras' in producto else ''
        nombre_producto = producto['nombre_producto'] if 'nombre_producto' in producto else ''
        if codigo_barras:
            # Verificar imagen del producto en background
            verificar_imagen_producto(codigo_barras, nombre_producto)
    
    cursor.close()
    conn.close()
    return productos

def contar_productos_sucursal(
    sucursal_uuid='22C8131D-4431-4E9A-AA04-ED188217C549',
    departamento=None,
    categoria=None,
    query=None
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = '''
        SELECT COUNT(*)
        FROM producto p
        JOIN producto_sucursal ps ON p.uuid_producto = ps.uuid_producto
        LEFT JOIN departamento d ON p.uuid_departamento = d.uuid_departamento
        LEFT JOIN categoria c ON p.uuid_categoria = c.uuid_categoria
        WHERE ps.uuid_sucursal = %s
          AND ps.existencia >= 1
          AND p.is_active = 1
          AND ps.is_active = 1
    '''
    params = [sucursal_uuid]
    
    # Lógica especial para "ofertas" - productos con descuento
    if categoria == 'ofertas':
        sql += ' AND ps.precio_venta2 > 0 AND ps.precio_venta2 < ps.precio_venta'
    elif departamento:
        sql += ' AND d.nombre_dep = %s'
        params.append(departamento)
    elif categoria:
        sql += ' AND c.nombre_categoria = %s'
        params.append(categoria)
    
    if query:
        sql += ' AND (LOWER(p.nombre_producto) LIKE %s OR LOWER(c.nombre_categoria) LIKE %s OR LOWER(d.nombre_dep) LIKE %s)'
        palabra = f"%{query.strip().lower()}%"
        params.extend([palabra, palabra, palabra])
    
    cursor.execute(sql, params)
    total = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    return total


def obtener_departamentos():
    """
    Obtiene la lista de departamentos únicos de la tabla departamento.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT nombre_dep FROM departamento ORDER BY nombre_dep")
        departamentos = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return departamentos
    except Exception as e:
        print(f"Error obteniendo departamentos: {e}")
        return []


def obtener_categorias(departamento=None):
    """
    Obtiene la lista de categorías.
    Si se proporciona departamento, filtra por ese departamento.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if departamento:
            sql = """
                SELECT DISTINCT c.nombre_categoria 
                FROM categoria c
                JOIN departamento d ON c.id_depto = d.id_depto
                WHERE d.nombre_dep = %s
                ORDER BY c.nombre_categoria
            """
            cursor.execute(sql, (departamento,))
        else:
            cursor.execute("SELECT DISTINCT nombre_categoria FROM categoria ORDER BY nombre_categoria")
        
        categorias = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return categorias
    except Exception as e:
        print(f"Error obteniendo categorías: {e}")
        return []


def consultar_puntos_cliente(busqueda):
    """
    Consulta los puntos de un cliente por teléfono, código o ID.
    Retorna (dict_cliente, None) si encuentra el cliente, o (None, mensaje_error) si no.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT nombre, apellidos, puntos 
            FROM cliente 
            WHERE is_active=1 AND (idcliente = %s OR telefono = %s OR vCodigoCliente = %s) 
            LIMIT 1
        """
        cursor.execute(query, (busqueda, busqueda, busqueda))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return row, None
        else:
            return None, "Cliente no encontrado."
    except Exception as e:
        return None, f"Error al consultar: {e}"

