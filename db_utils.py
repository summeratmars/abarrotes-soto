"""
db_utils.py - Módulo de acceso a base de datos azula_pdv (MariaDB)
Adaptado a la nueva estructura del punto de venta Azula PDV.
Usa aliases SQL para mantener compatibilidad con los templates existentes.
"""
import json
import re
import os
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def get_db_connection():
    """Obtiene conexión a la base de datos MariaDB azula_pdv."""
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'root'),
        database=os.environ.get('DB_NAME', 'azula_pdv'),
        port=int(os.environ.get('DB_PORT', '3306'))
    )

# ---------------------------------------------------------------------------
# GUARDAR PEDIDO ONLINE (reemplaza guardar_cotizacion_web)
# ---------------------------------------------------------------------------
def guardar_cotizacion_web(carrito, observaciones="Generado por tienda en línea"):
    """
    Guarda un pedido online en las tablas pedidos_online + detalles_pedido_online.
    Retorna (numero_pedido, pedido_id) en lugar de (folio, uuid_cotizacion).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Generar número de pedido único
        cursor.execute("SELECT MAX(id) AS max_id FROM pedidos_online")
        row = cursor.fetchone()
        next_id = (row['max_id'] or 0) + 1
        numero_pedido = f"WEB-{next_id:06d}"

        # Calcular totales consultando info completa de BD
        productos = []
        subtotal = 0.0
        descuento_total = 0.0

        for prod in carrito:
            cantidad = float(prod.get('cantidad', 1))
            codigo_barras = prod.get('cbarras') or prod.get('codigo_barras') or prod.get('codigo') or ""

            # Consultar información completa del producto desde BD
            cursor.execute('''
                SELECT p.id, p.codigo_barras, p.nombre, p.precio_venta, p.unidad_medida
                FROM productos p
                WHERE (p.codigo_barras = %s OR p.codigo = %s) AND p.activo = 1
                LIMIT 1
            ''', (codigo_barras, codigo_barras))
            producto_info = cursor.fetchone()

            if producto_info:
                producto_id = producto_info['id']
                precio_venta = float(producto_info['precio_venta'])
                nombre_producto = producto_info['nombre']

                # Buscar precio escalonado aplicable
                cursor.execute('''
                    SELECT precio, cantidad_minima
                    FROM precios_escalonados
                    WHERE producto_id = %s AND activo = 1
                    ORDER BY cantidad_minima DESC
                ''', (producto_id,))
                precios_esc = cursor.fetchall()

                precio_aplicable = precio_venta
                descuento_unitario = 0.0

                for pe in precios_esc:
                    if cantidad >= float(pe['cantidad_minima']):
                        precio_aplicable = float(pe['precio'])
                        descuento_unitario = precio_venta - precio_aplicable
                        break

                subtotal_prod = cantidad * precio_venta
                descuento_prod = cantidad * descuento_unitario

                productos.append({
                    "producto_id": producto_id,
                    "codigo_barras": codigo_barras,
                    "nombre": nombre_producto,
                    "cantidad": cantidad,
                    "precio_unitario": precio_aplicable,
                    "descuento": descuento_unitario,
                    "subtotal": cantidad * precio_aplicable,
                    "importe_original": subtotal_prod,
                    "unidad": producto_info['unidad_medida'] or "PZA"
                })

                subtotal += subtotal_prod
                descuento_total += descuento_prod
            else:
                # Fallback si no encontramos el producto en BD
                precio = float(prod.get('precio', 0))
                subtotal_prod = cantidad * precio
                productos.append({
                    "producto_id": None,
                    "codigo_barras": codigo_barras,
                    "nombre": prod.get('nombre') or prod.get('nombre_producto') or "",
                    "cantidad": cantidad,
                    "precio_unitario": precio,
                    "descuento": 0,
                    "subtotal": subtotal_prod,
                    "importe_original": subtotal_prod,
                    "unidad": "PZA"
                })
                subtotal += subtotal_prod

        total = subtotal - descuento_total

        # Insertar pedido online
        sql_pedido = """
            INSERT INTO pedidos_online (
                numero_pedido, cliente_nombre, subtotal, descuento, total,
                estado, notas
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_pedido, (
            numero_pedido,
            'Cliente Online',
            subtotal,
            descuento_total,
            total,
            'Pendiente',
            observaciones
        ))
        pedido_id = cursor.lastrowid

        # Insertar detalles
        for p in productos:
            sql_detalle = """
                INSERT INTO detalles_pedido_online (
                    pedido_id, producto_id, nombre_producto, cantidad,
                    precio_unitario, descuento, subtotal
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_detalle, (
                pedido_id,
                p['producto_id'],
                p['nombre'],
                p['cantidad'],
                p['precio_unitario'],
                p['descuento'],
                p['subtotal']
            ))

        conn.commit()
        # Retorna (folio, uuid) para compatibilidad - usamos numero_pedido como folio
        return numero_pedido, str(pedido_id)
    except Exception as e:
        conn.rollback()
        print(f"Error al guardar pedido online: {e}")
        return None, None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# REGISTRAR CLIENTE
# ---------------------------------------------------------------------------
def registrar_cliente_monedero(nombre_completo, telefono):
    """
    Registra un cliente nuevo en la tabla clientes.
    Retorna (dict_cliente, None) o (None, error_msg).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Validar que el teléfono no exista
        cursor.execute(
            "SELECT id FROM clientes WHERE telefono = %s AND activo = 1 LIMIT 1",
            (telefono,)
        )
        if cursor.fetchone():
            return None, "El teléfono ya está registrado."

        # Separar nombre y apellidos
        partes = re.split(r'\s+', nombre_completo.strip())
        if len(partes) == 1:
            nombre = partes[0]
            apellido = ''
        elif len(partes) == 2:
            nombre, apellido = partes
        else:
            nombre = partes[0]
            apellido = ' '.join(partes[1:])

        sql = """
            INSERT INTO clientes (nombre, apellido, telefono, activo)
            VALUES (%s, %s, %s, 1)
        """
        cursor.execute(sql, (nombre, apellido, telefono))
        cliente_id = cursor.lastrowid

        # Generar código de cliente compatible
        vCodigoCliente = f"CLI{cliente_id:05d}"

        conn.commit()
        return {
            'idcliente': cliente_id,
            'vCodigoCliente': vCodigoCliente,
            'nombre': nombre,
            'apellidos': apellido
        }, None
    except Exception as e:
        conn.rollback()
        return None, f"Error al registrar: {e}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# GUARDAR PEDIDO CON DATOS DE ENTREGA
# ---------------------------------------------------------------------------
def guardar_pedido_db(nombre, direccion, colonia, telefono, numero_cliente, pago, carrito):
    """
    Guarda el pedido completo con datos de entrega en pedidos_online + detalles.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Generar número de pedido
        cursor.execute("SELECT MAX(id) AS max_id FROM pedidos_online")
        row = cursor.fetchone()
        next_id = (row['max_id'] or 0) + 1
        numero_pedido = f"WEB-{next_id:06d}"

        # Calcular total
        total = sum(float(p.get('precio', 0)) * float(p.get('cantidad', 1)) for p in carrito)

        direccion_completa = f"{direccion}, Col. {colonia}" if colonia else direccion

        sql_pedido = """
            INSERT INTO pedidos_online (
                numero_pedido, cliente_nombre, cliente_telefono,
                direccion, subtotal, total, estado, metodo_pago, notas
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_pedido, (
            numero_pedido, nombre, telefono,
            direccion_completa, total, total, 'Pendiente', pago,
            f"Cliente: {numero_cliente}" if numero_cliente else None
        ))
        pedido_id = cursor.lastrowid

        # Insertar detalles
        for prod in carrito:
            cantidad = float(prod.get('cantidad', 1))
            precio = float(prod.get('precio', 0))
            nombre_prod = prod.get('nombre') or prod.get('nombre_producto') or ''
            codigo = prod.get('cbarras') or prod.get('codigo_barras') or ''

            # Buscar producto_id en BD
            producto_id = None
            if codigo:
                cursor.execute(
                    "SELECT id FROM productos WHERE (codigo_barras = %s OR codigo = %s) AND activo = 1 LIMIT 1",
                    (codigo, codigo)
                )
                r = cursor.fetchone()
                if r:
                    producto_id = r['id']

            sql_det = """
                INSERT INTO detalles_pedido_online (
                    pedido_id, producto_id, nombre_producto, cantidad,
                    precio_unitario, descuento, subtotal
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_det, (
                pedido_id, producto_id, nombre_prod, cantidad,
                precio, 0, cantidad * precio
            ))

        conn.commit()
        return pedido_id
    except Exception as e:
        conn.rollback()
        print(f"Error al guardar pedido: {e}")
        return None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# OBTENER PRODUCTOS (con aliases para compatibilidad con templates)
# ---------------------------------------------------------------------------
def obtener_productos_sucursal(
    sucursal_uuid=None,  # ignorado en nueva BD (una sola sucursal)
    departamento=None,
    categoria=None,
    query=None,
    orden=None,
    pagina=1,
    por_pagina=None
):
    """
    Obtiene productos de la BD azula_pdv.
    Retorna dicts con los mismos nombres de campo que esperan los templates:
      cbarras, nombre_producto, precio_venta, precio_venta2, dCantMinPP2,
      precio_venta3, dCantMinPP3, existencia, puntos_lealtad,
      nombre_departamento, nombre_categoria, nombre_unidad
    """
    print(f"🔍 DEBUG obtener_productos_sucursal():")
    print(f"   departamento: '{departamento}'")
    print(f"   categoria: '{categoria}'")
    print(f"   query: '{query}'")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = '''
        SELECT
            p.codigo_barras AS cbarras,
            p.nombre        AS nombre_producto,
            p.precio_venta,
            p.stock          AS existencia,
            p.puntos_lealtad,
            p.unidad_medida  AS nombre_unidad,
            p.id             AS producto_id,
            d.nombre         AS nombre_departamento,
            c.nombre         AS nombre_categoria
        FROM productos p
        LEFT JOIN categorias c     ON p.categoria_id = c.id
        LEFT JOIN departamentos d  ON p.departamento_id = d.id
        WHERE p.stock >= 1
          AND p.activo = 1
    '''
    params = []

    if departamento:
        sql += ' AND d.nombre = %s'
        params.append(departamento)

    if categoria:
        if categoria.lower() == 'ofertas':
            # Productos que tienen precio escalonado menor al precio normal
            sql += ''' AND EXISTS (
                SELECT 1 FROM precios_escalonados pe
                WHERE pe.producto_id = p.id AND pe.activo = 1 AND pe.precio < p.precio_venta
            )'''
        else:
            sql += ' AND c.nombre = %s'
            params.append(categoria)

    if query:
        sql += ' AND (LOWER(p.nombre) LIKE %s OR LOWER(c.nombre) LIKE %s OR LOWER(d.nombre) LIKE %s)'
        palabra = f"%{query.strip().lower()}%"
        params.extend([palabra, palabra, palabra])

    if orden == 'nombre_asc':
        sql += ' ORDER BY p.nombre ASC'
    elif orden == 'precio_asc':
        sql += ' ORDER BY p.precio_venta ASC'
    elif orden == 'precio_desc':
        sql += ' ORDER BY p.precio_venta DESC'

    if por_pagina:
        offset = (pagina - 1) * por_pagina
        sql += f' LIMIT {por_pagina} OFFSET {offset}'

    cursor.execute(sql, params)
    productos_raw = cursor.fetchall()

    # Obtener precios escalonados para todos los productos de una vez
    product_ids = [p['producto_id'] for p in productos_raw if p.get('producto_id')]
    precios_map = {}
    if product_ids:
        placeholders = ','.join(['%s'] * len(product_ids))
        cursor.execute(f'''
            SELECT producto_id, precio, cantidad_minima, nombre
            FROM precios_escalonados
            WHERE producto_id IN ({placeholders}) AND activo = 1
            ORDER BY producto_id, cantidad_minima ASC
        ''', product_ids)
        for pe in cursor.fetchall():
            pid = pe['producto_id']
            if pid not in precios_map:
                precios_map[pid] = []
            precios_map[pid].append(pe)

    # Enriquecer productos con precios escalonados (compatibilidad)
    productos = []
    for p in productos_raw:
        pid = p.get('producto_id')
        escalados = precios_map.get(pid, [])

        # precio_venta2 / dCantMinPP2 = primer precio escalonado
        if len(escalados) >= 1:
            p['precio_venta2'] = float(escalados[0]['precio'])
            p['dCantMinPP2'] = float(escalados[0]['cantidad_minima'])
        else:
            p['precio_venta2'] = 0
            p['dCantMinPP2'] = 0

        # precio_venta3 / dCantMinPP3 = segundo precio escalonado
        if len(escalados) >= 2:
            p['precio_venta3'] = float(escalados[1]['precio'])
            p['dCantMinPP3'] = float(escalados[1]['cantidad_minima'])
        else:
            p['precio_venta3'] = 0
            p['dCantMinPP3'] = 0

        # Asegurar tipos correctos
        p['precio_venta'] = float(p['precio_venta'])
        p['existencia'] = float(p['existencia'])
        p['puntos_lealtad'] = p['puntos_lealtad'] or 0

        productos.append(p)

    cursor.close()
    conn.close()
    return productos


# ---------------------------------------------------------------------------
# CONTAR PRODUCTOS
# ---------------------------------------------------------------------------
def contar_productos_sucursal(
    sucursal_uuid=None,
    departamento=None,
    categoria=None,
    query=None
):
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = '''
        SELECT COUNT(*)
        FROM productos p
        LEFT JOIN departamentos d ON p.departamento_id = d.id
        LEFT JOIN categorias c    ON p.categoria_id = c.id
        WHERE p.stock >= 1
          AND p.activo = 1
    '''
    params = []

    if categoria and categoria.lower() == 'ofertas':
        sql += ''' AND EXISTS (
            SELECT 1 FROM precios_escalonados pe
            WHERE pe.producto_id = p.id AND pe.activo = 1 AND pe.precio < p.precio_venta
        )'''
    elif departamento:
        sql += ' AND d.nombre = %s'
        params.append(departamento)
    elif categoria:
        sql += ' AND c.nombre = %s'
        params.append(categoria)

    if query:
        sql += ' AND (LOWER(p.nombre) LIKE %s OR LOWER(c.nombre) LIKE %s OR LOWER(d.nombre) LIKE %s)'
        palabra = f"%{query.strip().lower()}%"
        params.extend([palabra, palabra, palabra])

    cursor.execute(sql, params)
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return total


# ---------------------------------------------------------------------------
# DEPARTAMENTOS Y CATEGORÍAS
# ---------------------------------------------------------------------------
def obtener_departamentos():
    """Obtiene departamentos activos."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM departamentos WHERE activo = 1 ORDER BY nombre")
        departamentos = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return departamentos
    except Exception as e:
        print(f"Error obteniendo departamentos: {e}")
        return []


def obtener_categorias(departamento=None):
    """Obtiene categorías activas, opcionalmente filtradas por departamento."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if departamento:
            sql = """
                SELECT DISTINCT c.nombre
                FROM categorias c
                JOIN departamentos d ON c.departamento_id = d.id
                WHERE d.nombre = %s AND c.activo = 1
                ORDER BY c.nombre
            """
            cursor.execute(sql, (departamento,))
        else:
            cursor.execute("SELECT nombre FROM categorias WHERE activo = 1 ORDER BY nombre")

        categorias = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return categorias
    except Exception as e:
        print(f"Error obteniendo categorías: {e}")
        return []


# ---------------------------------------------------------------------------
# CONSULTAR PUNTOS DE CLIENTE
# ---------------------------------------------------------------------------
def consultar_puntos_cliente(busqueda):
    """
    Consulta puntos de un cliente por teléfono o ID.
    Retorna (dict_cliente, None) o (None, mensaje_error).
    Compatible con el formato esperado por app.py (nombre, apellidos, puntos).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT nombre, apellido AS apellidos, puntos_lealtad AS puntos
            FROM clientes
            WHERE activo = 1 AND (id = %s OR telefono = %s)
            LIMIT 1
        """
        # Intentar buscar por ID numérico o por teléfono
        try:
            busqueda_id = int(busqueda)
        except (ValueError, TypeError):
            busqueda_id = 0

        cursor.execute(query, (busqueda_id, busqueda))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            return row, None
        else:
            return None, "Cliente no encontrado."
    except Exception as e:
        return None, f"Error al consultar: {e}"


# ---------------------------------------------------------------------------
# FUNCIONES AUXILIARES PARA ADMIN
# ---------------------------------------------------------------------------
def obtener_producto_por_codigo(codigo_barras):
    """Obtiene un producto completo por código de barras."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT
            p.id, p.codigo, p.codigo_barras AS cbarras, p.nombre AS nombre_producto,
            p.precio_venta, p.stock AS existencia, p.unidad_medida,
            p.categoria_id, p.departamento_id, p.imagen_url,
            p.puntos_lealtad, p.activo,
            d.nombre AS nombre_departamento, d.nombre AS nombre_dep,
            c.nombre AS nombre_categoria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN departamentos d ON p.departamento_id = d.id
        WHERE p.codigo_barras = %s OR p.codigo = %s
        LIMIT 1
    ''', (codigo_barras, codigo_barras))
    producto = cursor.fetchone()

    if producto:
        # Agregar precio escalonado
        cursor.execute('''
            SELECT precio, cantidad_minima FROM precios_escalonados
            WHERE producto_id = %s AND activo = 1
            ORDER BY cantidad_minima ASC LIMIT 1
        ''', (producto['id'],))
        pe = cursor.fetchone()
        producto['precio_venta2'] = float(pe['precio']) if pe else 0
        producto['dCantMinPP2'] = float(pe['cantidad_minima']) if pe else 0

    cursor.close()
    conn.close()
    return producto


def obtener_todos_productos_admin(pagina=1, por_pagina=50):
    """Obtiene productos paginados para el panel admin."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    offset = (pagina - 1) * por_pagina

    cursor.execute('''
        SELECT
            p.id, p.codigo_barras AS cbarras, p.nombre AS nombre_producto,
            p.precio_venta, p.stock AS existencia,
            d.nombre AS nombre_dep,
            c.nombre AS nombre_categoria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN departamentos d ON p.departamento_id = d.id
        WHERE p.activo = 1
        ORDER BY p.nombre ASC
        LIMIT %s OFFSET %s
    ''', (por_pagina, offset))
    productos = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
    total = cursor.fetchone()['COUNT(*)']

    cursor.close()
    conn.close()
    return productos, total


def crear_producto_db(datos):
    """Crea un nuevo producto en la BD."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verificar si el código de barras ya existe
        cursor.execute(
            "SELECT id FROM productos WHERE codigo_barras = %s LIMIT 1",
            (datos['cbarras'],)
        )
        if cursor.fetchone():
            return None, f"El código de barras {datos['cbarras']} ya existe"

        # Buscar o crear categoría y departamento
        cat_id = _get_or_create_categoria(cursor, datos.get('nombre_categoria'), datos.get('nombre_dep'))
        dep_id = _get_or_create_departamento(cursor, datos.get('nombre_dep'))

        sql = """
            INSERT INTO productos (
                codigo, codigo_barras, nombre, precio_venta, stock,
                unidad_medida, categoria_id, departamento_id, imagen_url, activo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """
        cursor.execute(sql, (
            datos['cbarras'],  # usar código de barras como código también
            datos['cbarras'],
            datos['nombre_producto'],
            datos['precio_venta'],
            datos.get('existencia', 0),
            datos.get('unidad_medida', 'PZA'),
            cat_id,
            dep_id,
            datos.get('imagen')
        ))
        producto_id = cursor.lastrowid

        # Crear precio escalonado si hay precio_venta2
        if datos.get('precio_venta2') and float(datos['precio_venta2']) > 0:
            cursor.execute("""
                INSERT INTO precios_escalonados (producto_id, nombre, cantidad_minima, precio, activo)
                VALUES (%s, 'Precio 2', 1, %s, 1)
            """, (producto_id, datos['precio_venta2']))

        conn.commit()
        return producto_id, None
    except Exception as e:
        conn.rollback()
        return None, f"Error al crear producto: {e}"
    finally:
        cursor.close()
        conn.close()


def actualizar_producto_db(codigo_barras, datos):
    """Actualiza un producto existente en la BD."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Buscar producto
        cursor.execute(
            "SELECT id FROM productos WHERE (codigo_barras = %s OR codigo = %s) LIMIT 1",
            (codigo_barras, codigo_barras)
        )
        prod = cursor.fetchone()
        if not prod:
            return False, "Producto no encontrado"

        producto_id = prod['id']

        cat_id = _get_or_create_categoria(cursor, datos.get('nombre_categoria'), datos.get('nombre_dep'))
        dep_id = _get_or_create_departamento(cursor, datos.get('nombre_dep'))

        sql = """
            UPDATE productos SET
                nombre = %s, precio_venta = %s, stock = %s,
                categoria_id = %s, departamento_id = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            datos['nombre_producto'],
            datos['precio_venta'],
            datos.get('existencia', 0),
            cat_id,
            dep_id,
            producto_id
        ))

        # Actualizar o crear precio escalonado
        precio_venta2 = float(datos.get('precio_venta2', 0))
        if precio_venta2 > 0:
            cursor.execute(
                "SELECT id FROM precios_escalonados WHERE producto_id = %s AND nombre = 'Precio 2' LIMIT 1",
                (producto_id,)
            )
            pe = cursor.fetchone()
            if pe:
                cursor.execute(
                    "UPDATE precios_escalonados SET precio = %s, activo = 1 WHERE id = %s",
                    (precio_venta2, pe['id'])
                )
            else:
                cursor.execute("""
                    INSERT INTO precios_escalonados (producto_id, nombre, cantidad_minima, precio, activo)
                    VALUES (%s, 'Precio 2', 1, %s, 1)
                """, (producto_id, precio_venta2))
        else:
            # Desactivar precio escalonado si no hay
            cursor.execute(
                "UPDATE precios_escalonados SET activo = 0 WHERE producto_id = %s AND nombre = 'Precio 2'",
                (producto_id,)
            )

        # Actualizar imagen si se proporciona
        if datos.get('imagen'):
            cursor.execute(
                "UPDATE productos SET imagen_url = %s WHERE id = %s",
                (datos['imagen'], producto_id)
            )

        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, f"Error al actualizar: {e}"
    finally:
        cursor.close()
        conn.close()


def eliminar_producto_db(codigo_barras):
    """Desactiva un producto (soft delete)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE productos SET activo = 0 WHERE codigo_barras = %s OR codigo = %s",
            (codigo_barras, codigo_barras)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar producto: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def obtener_productos_bajo_stock(limite=5):
    """Obtiene productos con stock menor al límite."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT
            p.codigo_barras AS cbarras, p.nombre AS nombre_producto,
            p.precio_venta, p.stock AS existencia,
            d.nombre AS nombre_dep, c.nombre AS nombre_categoria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN departamentos d ON p.departamento_id = d.id
        WHERE p.activo = 1 AND p.stock < %s AND p.stock > 0
        ORDER BY p.stock ASC
    ''', (limite,))
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos


def obtener_estadisticas_admin():
    """Obtiene estadísticas para el dashboard admin."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    stats = {}

    cursor.execute("SELECT COUNT(*) AS total FROM productos WHERE activo = 1")
    stats['total_productos'] = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM clientes WHERE activo = 1")
    stats['total_clientes'] = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM pedidos_online WHERE estado = 'Pendiente'")
    stats['pedidos_pendientes'] = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COALESCE(SUM(total), 0) AS total_ventas
        FROM ventas
        WHERE estado = 'Completada'
          AND MONTH(fecha_venta) = MONTH(CURDATE())
          AND YEAR(fecha_venta) = YEAR(CURDATE())
    """)
    stats['ventas_mes'] = float(cursor.fetchone()['total_ventas'])

    cursor.execute("""
        SELECT numero_pedido AS id, cliente_nombre AS nombre,
               DATE_FORMAT(fecha_pedido, '%%d/%%m/%%Y %%H:%%i') AS fecha,
               total, estado
        FROM pedidos_online
        ORDER BY fecha_pedido DESC LIMIT 5
    """)
    stats['ultimos_pedidos'] = cursor.fetchall()

    cursor.close()
    conn.close()
    return stats


def obtener_pedidos_admin():
    """Obtiene todos los pedidos online para el admin."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, numero_pedido, cliente_nombre AS nombre,
               cliente_telefono AS telefono,
               direccion, metodo_pago,
               DATE_FORMAT(fecha_pedido, '%%d/%%m/%%Y %%H:%%i') AS fecha,
               total, estado
        FROM pedidos_online
        ORDER BY fecha_pedido DESC
    """)
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return pedidos


def actualizar_estado_pedido(pedido_id, nuevo_estado):
    """Actualiza el estado de un pedido online."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if nuevo_estado in ('En proceso', 'Enviado', 'Entregado'):
            cursor.execute(
                "UPDATE pedidos_online SET estado = %s, fecha_procesado = NOW() WHERE id = %s OR numero_pedido = %s",
                (nuevo_estado, pedido_id, pedido_id)
            )
        else:
            cursor.execute(
                "UPDATE pedidos_online SET estado = %s WHERE id = %s OR numero_pedido = %s",
                (nuevo_estado, pedido_id, pedido_id)
            )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error actualizando estado: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# HELPERS PRIVADOS
# ---------------------------------------------------------------------------
def _get_or_create_departamento(cursor, nombre_dep):
    """Busca o crea un departamento, retorna su ID."""
    if not nombre_dep:
        return None
    cursor.execute("SELECT id FROM departamentos WHERE nombre = %s LIMIT 1", (nombre_dep,))
    row = cursor.fetchone()
    if row:
        return row['id']
    cursor.execute("INSERT INTO departamentos (nombre, activo) VALUES (%s, 1)", (nombre_dep,))
    return cursor.lastrowid


def _get_or_create_categoria(cursor, nombre_cat, nombre_dep=None):
    """Busca o crea una categoría, retorna su ID."""
    if not nombre_cat:
        return None

    dep_id = _get_or_create_departamento(cursor, nombre_dep) if nombre_dep else None

    if dep_id:
        cursor.execute(
            "SELECT id FROM categorias WHERE nombre = %s AND departamento_id = %s LIMIT 1",
            (nombre_cat, dep_id)
        )
    else:
        cursor.execute("SELECT id FROM categorias WHERE nombre = %s LIMIT 1", (nombre_cat,))
    row = cursor.fetchone()
    if row:
        return row['id']

    cursor.execute(
        "INSERT INTO categorias (nombre, departamento_id, activo) VALUES (%s, %s, 1)",
        (nombre_cat, dep_id)
    )
    return cursor.lastrowid

