"""
API REST Local para Abarrotes Soto
Expone endpoints que permiten acceder a la base de datos azula_pdv (MariaDB)
sin necesidad de exponer directamente el puerto de MySQL.
Adaptado a la nueva estructura del punto de venta Azula PDV.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import mysql.connector
from mysql.connector import Error, pooling
import os
import json
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Pool de conexiones para mejorar rendimiento
connection_pool = pooling.MySQLConnectionPool(
    pool_name="abarrotes_pool",
    pool_size=10,
    pool_reset_session=True,
    host=os.environ.get('DB_HOST', 'localhost'),
    user=os.environ.get('DB_USER', 'root'),
    password=os.environ.get('DB_PASSWORD', 'root'),
    database=os.environ.get('DB_NAME', 'azula_pdv'),
    port=int(os.environ.get('DB_PORT', '3306'))
)

app = FastAPI(
    title="Abarrotes Soto DB API",
    description="API REST para acceso a la base de datos azula_pdv de Abarrotes Soto",
    version="2.0.0"
)

# Configurar CORS para permitir peticiones desde Render/Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Modelos Pydantic
# ---------------------------------------------------------------------------
class ProductoCarrito(BaseModel):
    nombre: str
    cantidad: float
    precio: float
    precio_original: Optional[float] = None
    cbarras: Optional[str] = None
    codigo_barras: Optional[str] = None
    codigo: Optional[str] = None

class CotizacionRequest(BaseModel):
    carrito: List[ProductoCarrito]
    observaciones: str = "Generado por tienda en línea"

class ClienteMonederoRequest(BaseModel):
    nombre_completo: str
    telefono: str

class PedidoRequest(BaseModel):
    nombre: str
    direccion: str
    colonia: str
    telefono: str
    numero_cliente: Optional[str] = ""
    pago: str
    carrito: List[ProductoCarrito]

class ProductoAdminRequest(BaseModel):
    cbarras: str
    nombre_producto: str
    precio_venta: float
    existencia: Optional[float] = 0
    nombre_categoria: Optional[str] = None
    nombre_dep: Optional[str] = None
    unidad_medida: Optional[str] = "PZA"
    precio_venta2: Optional[float] = 0
    imagen: Optional[str] = None

class EstadoPedidoRequest(BaseModel):
    nuevo_estado: str

# ---------------------------------------------------------------------------
# Función auxiliar para conectar a la BD usando el pool
# ---------------------------------------------------------------------------
def get_db_connection():
    try:
        return connection_pool.get_connection()
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise HTTPException(status_code=500, detail=f"Error de conexión a base de datos: {str(e)}")


# ---------------------------------------------------------------------------
# Endpoints básicos
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return {
        "message": "API de Abarrotes Soto funcionando correctamente",
        "version": "2.0.0",
        "database": "azula_pdv",
        "status": "online"
    }

@app.get("/health")
def health_check():
    """Verificar el estado de la API y la conexión a la base de datos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error de salud: {str(e)}")


# ---------------------------------------------------------------------------
# PRODUCTOS
# ---------------------------------------------------------------------------
@app.get("/api/productos")
def obtener_productos(
    sucursal_uuid: Optional[str] = None,  # ignorado - una sola sucursal
    departamento: Optional[str] = None,
    categoria: Optional[str] = None,
    query: Optional[str] = None,
    orden: Optional[str] = None,
    pagina: int = 1,
    por_pagina: Optional[int] = None
):
    """Obtener productos con filtros opcionales. Retorna aliases compatibles con templates."""
    conn = get_db_connection()
    try:
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

        # Obtener precios escalonados en batch
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

        # Enriquecer con precios escalonados (compatibilidad con templates)
        productos = []
        for p in productos_raw:
            pid = p.get('producto_id')
            escalados = precios_map.get(pid, [])

            if len(escalados) >= 1:
                p['precio_venta2'] = float(escalados[0]['precio'])
                p['dCantMinPP2'] = float(escalados[0]['cantidad_minima'])
            else:
                p['precio_venta2'] = 0
                p['dCantMinPP2'] = 0

            if len(escalados) >= 2:
                p['precio_venta3'] = float(escalados[1]['precio'])
                p['dCantMinPP3'] = float(escalados[1]['cantidad_minima'])
            else:
                p['precio_venta3'] = 0
                p['dCantMinPP3'] = 0

            p['precio_venta'] = float(p['precio_venta'])
            p['existencia'] = float(p['existencia'])
            p['puntos_lealtad'] = p['puntos_lealtad'] or 0

            productos.append(p)

        cursor.close()
        conn.close()
        return {"productos": productos}
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")


@app.get("/api/productos/count")
def contar_productos(
    sucursal_uuid: Optional[str] = None,
    departamento: Optional[str] = None,
    categoria: Optional[str] = None,
    query: Optional[str] = None
):
    """Contar productos según filtros"""
    conn = get_db_connection()
    try:
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
        return {"total": total}
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al contar productos: {str(e)}")


# ---------------------------------------------------------------------------
# DEPARTAMENTOS Y CATEGORÍAS
# ---------------------------------------------------------------------------
@app.get("/api/departamentos")
def obtener_departamentos():
    """Obtener lista de departamentos activos"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM departamentos WHERE activo = 1 ORDER BY nombre")
        departamentos = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"departamentos": departamentos}
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al obtener departamentos: {str(e)}")

@app.get("/api/categorias")
def obtener_categorias(departamento: Optional[str] = None):
    """Obtener categorías activas, opcionalmente filtradas por departamento"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if departamento:
            cursor.execute(
                """SELECT DISTINCT c.nombre
                   FROM categorias c
                   JOIN departamentos d ON c.departamento_id = d.id
                   WHERE d.nombre = %s AND c.activo = 1
                   ORDER BY c.nombre""",
                (departamento,)
            )
        else:
            cursor.execute("SELECT nombre FROM categorias WHERE activo = 1 ORDER BY nombre")
        categorias = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"categorias": categorias}
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al obtener categorías: {str(e)}")


# ---------------------------------------------------------------------------
# PEDIDO ONLINE (reemplaza cotización)
# ---------------------------------------------------------------------------
@app.post("/api/cotizacion")
def guardar_cotizacion(request: CotizacionRequest):
    """Guardar pedido online en la base de datos (compatibilidad endpoint /api/cotizacion)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Generar número de pedido único
        cursor.execute("SELECT MAX(id) AS max_id FROM pedidos_online")
        row = cursor.fetchone()
        next_id = (row['max_id'] or 0) + 1
        numero_pedido = f"WEB-{next_id:06d}"

        productos = []
        subtotal = 0.0
        descuento_total = 0.0

        for prod in request.carrito:
            cantidad = float(prod.cantidad)
            codigo_barras = prod.cbarras or prod.codigo_barras or prod.codigo or ""

            # Consultar información completa del producto
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
                precio = float(prod.precio)
                subtotal_prod = cantidad * precio
                productos.append({
                    "producto_id": None,
                    "codigo_barras": codigo_barras,
                    "nombre": prod.nombre,
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
            numero_pedido, 'Cliente Online', subtotal,
            descuento_total, total, 'Pendiente', request.observaciones
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
                pedido_id, p['producto_id'], p['nombre'], p['cantidad'],
                p['precio_unitario'], p['descuento'], p['subtotal']
            ))

        conn.commit()
        cursor.close()
        conn.close()
        # Retorna folio y uuid_cotizacion para compatibilidad con db_api_client
        return {"folio": numero_pedido, "uuid_cotizacion": str(pedido_id)}
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al guardar pedido online: {str(e)}")


# ---------------------------------------------------------------------------
# CLIENTES
# ---------------------------------------------------------------------------
@app.post("/api/cliente/monedero")
def registrar_cliente(request: ClienteMonederoRequest):
    """Registrar un nuevo cliente en la tabla clientes"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Validar que el teléfono no exista
        cursor.execute(
            "SELECT id FROM clientes WHERE telefono = %s AND activo = 1 LIMIT 1",
            (request.telefono,)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El teléfono ya está registrado")

        # Separar nombre y apellidos
        partes = re.split(r'\s+', request.nombre_completo.strip())
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
        cursor.execute(sql, (nombre, apellido, request.telefono))
        cliente_id = cursor.lastrowid

        vCodigoCliente = f"CLI{cliente_id:05d}"

        conn.commit()
        cursor.close()
        conn.close()

        return {
            'idcliente': cliente_id,
            'vCodigoCliente': vCodigoCliente,
            'nombre': nombre,
            'apellidos': apellido
        }
    except HTTPException:
        try:
            conn.close()
        except:
            pass
        raise
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al registrar cliente: {str(e)}")

@app.get("/api/cliente/puntos")
def consultar_puntos(busqueda: str):
    """Consultar puntos de un cliente por teléfono o ID"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        try:
            busqueda_id = int(busqueda)
        except (ValueError, TypeError):
            busqueda_id = 0

        cursor.execute(
            """SELECT nombre, apellido AS apellidos, puntos_lealtad AS puntos
               FROM clientes
               WHERE activo = 1 AND (id = %s OR telefono = %s)
               LIMIT 1""",
            (busqueda_id, busqueda)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return {
            "nombre": row.get('nombre', ''),
            "apellidos": row.get('apellidos', ''),
            "puntos": row.get('puntos', 0),
            "vCodigoCliente": ""
        }
    except HTTPException:
        raise
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al consultar puntos: {str(e)}")


# ---------------------------------------------------------------------------
# PEDIDO CON DATOS DE ENTREGA
# ---------------------------------------------------------------------------
@app.post("/api/pedido")
def guardar_pedido(request: PedidoRequest):
    """Guardar un pedido con datos de entrega"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Generar número de pedido
        cursor.execute("SELECT MAX(id) AS max_id FROM pedidos_online")
        row = cursor.fetchone()
        next_id = (row['max_id'] or 0) + 1
        numero_pedido = f"WEB-{next_id:06d}"

        # Calcular total
        total = sum(float(p.precio) * float(p.cantidad) for p in request.carrito)

        direccion_completa = f"{request.direccion}, Col. {request.colonia}" if request.colonia else request.direccion

        sql_pedido = """
            INSERT INTO pedidos_online (
                numero_pedido, cliente_nombre, cliente_telefono,
                direccion, subtotal, total, estado, metodo_pago, notas
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_pedido, (
            numero_pedido, request.nombre, request.telefono,
            direccion_completa, total, total, 'Pendiente', request.pago,
            f"Cliente: {request.numero_cliente}" if request.numero_cliente else None
        ))
        pedido_id = cursor.lastrowid

        # Insertar detalles
        for prod in request.carrito:
            cantidad = float(prod.cantidad)
            precio = float(prod.precio)
            nombre_prod = prod.nombre
            codigo = prod.cbarras or prod.codigo_barras or prod.codigo or ""

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
        cursor.close()
        conn.close()
        return {"pedido_id": pedido_id}
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al guardar pedido: {str(e)}")


# ---------------------------------------------------------------------------
# ADMIN: Estadísticas
# ---------------------------------------------------------------------------
@app.get("/api/admin/estadisticas")
def obtener_estadisticas():
    """Obtener estadísticas para el dashboard admin"""
    conn = get_db_connection()
    try:
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
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")


# ---------------------------------------------------------------------------
# ADMIN: Productos
# ---------------------------------------------------------------------------
@app.get("/api/admin/productos")
def obtener_productos_admin(pagina: int = 1, por_pagina: int = 50):
    """Obtener productos paginados para el panel admin"""
    conn = get_db_connection()
    try:
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

        cursor.execute("SELECT COUNT(*) AS total FROM productos WHERE activo = 1")
        total = cursor.fetchone()['total']

        cursor.close()
        conn.close()
        return {"productos": productos, "total": total}
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al obtener productos admin: {str(e)}")

@app.get("/api/admin/producto/{codigo_barras}")
def obtener_producto_por_codigo(codigo_barras: str):
    """Obtener producto completo por código de barras"""
    conn = get_db_connection()
    try:
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

        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

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
    except HTTPException:
        raise
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al obtener producto: {str(e)}")

@app.post("/api/admin/producto")
def crear_producto(request: ProductoAdminRequest):
    """Crear un nuevo producto"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Verificar duplicado
        cursor.execute("SELECT id FROM productos WHERE codigo_barras = %s LIMIT 1", (request.cbarras,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"El código de barras {request.cbarras} ya existe")

        cat_id = _get_or_create_categoria(cursor, request.nombre_categoria, request.nombre_dep)
        dep_id = _get_or_create_departamento(cursor, request.nombre_dep)

        sql = """
            INSERT INTO productos (
                codigo, codigo_barras, nombre, precio_venta, stock,
                unidad_medida, categoria_id, departamento_id, imagen_url, activo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """
        cursor.execute(sql, (
            request.cbarras, request.cbarras, request.nombre_producto,
            request.precio_venta, request.existencia,
            request.unidad_medida, cat_id, dep_id, request.imagen
        ))
        producto_id = cursor.lastrowid

        if request.precio_venta2 and float(request.precio_venta2) > 0:
            cursor.execute("""
                INSERT INTO precios_escalonados (producto_id, nombre, cantidad_minima, precio, activo)
                VALUES (%s, 'Precio 2', 1, %s, 1)
            """, (producto_id, request.precio_venta2))

        conn.commit()
        cursor.close()
        conn.close()
        return {"producto_id": producto_id}
    except HTTPException:
        raise
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {str(e)}")

@app.put("/api/admin/producto/{codigo_barras}")
def actualizar_producto(codigo_barras: str, request: ProductoAdminRequest):
    """Actualizar un producto existente"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM productos WHERE (codigo_barras = %s OR codigo = %s) LIMIT 1",
            (codigo_barras, codigo_barras)
        )
        prod = cursor.fetchone()
        if not prod:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        producto_id = prod['id']
        cat_id = _get_or_create_categoria(cursor, request.nombre_categoria, request.nombre_dep)
        dep_id = _get_or_create_departamento(cursor, request.nombre_dep)

        sql = """
            UPDATE productos SET
                nombre = %s, precio_venta = %s, stock = %s,
                categoria_id = %s, departamento_id = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            request.nombre_producto, request.precio_venta, request.existencia,
            cat_id, dep_id, producto_id
        ))

        # Actualizar precio escalonado
        precio_venta2 = float(request.precio_venta2 or 0)
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
            cursor.execute(
                "UPDATE precios_escalonados SET activo = 0 WHERE producto_id = %s AND nombre = 'Precio 2'",
                (producto_id,)
            )

        if request.imagen:
            cursor.execute(
                "UPDATE productos SET imagen_url = %s WHERE id = %s",
                (request.imagen, producto_id)
            )

        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al actualizar producto: {str(e)}")

@app.delete("/api/admin/producto/{codigo_barras}")
def eliminar_producto(codigo_barras: str):
    """Desactivar un producto (soft delete)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE productos SET activo = 0 WHERE codigo_barras = %s OR codigo = %s",
            (codigo_barras, codigo_barras)
        )
        rows = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        if rows == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error al eliminar producto: {str(e)}")


# ---------------------------------------------------------------------------
# ADMIN: Productos bajo stock
# ---------------------------------------------------------------------------
@app.get("/api/admin/productos/bajo-stock")
def productos_bajo_stock(limite: int = 5):
    """Obtener productos con stock bajo"""
    conn = get_db_connection()
    try:
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
        return {"productos": productos}
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ---------------------------------------------------------------------------
# ADMIN: Pedidos
# ---------------------------------------------------------------------------
@app.get("/api/admin/pedidos")
def obtener_pedidos_admin():
    """Obtener todos los pedidos online para admin"""
    conn = get_db_connection()
    try:
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
        return {"pedidos": pedidos}
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.put("/api/admin/pedido/{pedido_id}/estado")
def actualizar_estado_pedido(pedido_id: str, request: EstadoPedidoRequest):
    """Actualizar estado de un pedido"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if request.nuevo_estado in ('En proceso', 'Enviado', 'Entregado'):
            cursor.execute(
                "UPDATE pedidos_online SET estado = %s, fecha_procesado = NOW() WHERE id = %s OR numero_pedido = %s",
                (request.nuevo_estado, pedido_id, pedido_id)
            )
        else:
            cursor.execute(
                "UPDATE pedidos_online SET estado = %s WHERE id = %s OR numero_pedido = %s",
                (request.nuevo_estado, pedido_id, pedido_id)
            )
        rows = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        if rows == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ---------------------------------------------------------------------------
# Helpers privados
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


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
