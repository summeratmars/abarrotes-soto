"""
API REST Local para Abarrotes Soto
Expone endpoints que permiten acceder a la base de datos MySQL local
sin necesidad de exponer directamente el puerto de MySQL.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import mysql.connector
from mysql.connector import Error
import os
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="Abarrotes Soto DB API",
    description="API REST para acceso a la base de datos de Abarrotes Soto",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica tu dominio de Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para validación de datos
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
    sucursal_uuid: str = '22C8131D-4431-4E9A-AA04-ED188217C549'

class PedidoRequest(BaseModel):
    nombre: str
    direccion: str
    colonia: str
    telefono: str
    numero_cliente: Optional[str] = ""
    pago: str
    carrito: List[ProductoCarrito]

# Función auxiliar para conectar a la base de datos
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME'),
            port=int(os.environ.get('DB_PORT', '3306'))
        )
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise HTTPException(status_code=500, detail=f"Error de conexión a base de datos: {str(e)}")

@app.get("/")
def root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return {
        "message": "API de Abarrotes Soto funcionando correctamente",
        "version": "1.0.0",
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

@app.get("/api/productos")
def obtener_productos(
    sucursal_uuid: str = '22C8131D-4431-4E9A-AA04-ED188217C549',
    departamento: Optional[str] = None,
    categoria: Optional[str] = None,
    query: Optional[str] = None,
    orden: Optional[str] = None,
    pagina: int = 1,
    por_pagina: Optional[int] = None
):
    """Obtener productos de una sucursal con filtros opcionales"""
    conn = get_db_connection()
    try:
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
        
        if por_pagina:
            offset = (pagina - 1) * por_pagina
            sql += f' LIMIT {por_pagina} OFFSET {offset}'
        
        cursor.execute(sql, params)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"productos": productos}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")

@app.get("/api/productos/count")
def contar_productos(
    sucursal_uuid: str = '22C8131D-4431-4E9A-AA04-ED188217C549',
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
        return {"total": total}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al contar productos: {str(e)}")

@app.get("/api/departamentos")
def obtener_departamentos():
    """Obtener lista de departamentos únicos"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT nombre_dep FROM departamento WHERE nombre_dep IS NOT NULL ORDER BY nombre_dep")
        departamentos = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"departamentos": departamentos}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al obtener departamentos: {str(e)}")

@app.get("/api/categorias")
def obtener_categorias(departamento: Optional[str] = None):
    """Obtener categorías, opcionalmente filtradas por departamento"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if departamento:
            cursor.execute(
                "SELECT DISTINCT nombre_categoria FROM categoria WHERE nombre_categoria IS NOT NULL AND uuid_departamento = (SELECT uuid_departamento FROM departamento WHERE nombre_dep = %s LIMIT 1) ORDER BY nombre_categoria",
                (departamento,)
            )
        else:
            cursor.execute("SELECT DISTINCT nombre_categoria FROM categoria WHERE nombre_categoria IS NOT NULL ORDER BY nombre_categoria")
        categorias = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"categorias": categorias}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al obtener categorías: {str(e)}")

@app.post("/api/cotizacion")
def guardar_cotizacion(request: CotizacionRequest):
    """Guardar cotización web en la base de datos"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Obtener próximo folio
        cursor.execute("SELECT MAX(CAST(folio AS UNSIGNED)) FROM cotizacion WHERE folio REGEXP '^[0-9]+$'")
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
        
        for prod in request.carrito:
            cantidad = float(prod.cantidad)
            codigo_barras = prod.cbarras or prod.codigo_barras or prod.codigo or ""
            
            # Consultar información completa del producto
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
                precio_venta3 = float(producto_info[7]) if producto_info[7] else 0.0
                dcantminpp3 = float(producto_info[8]) if producto_info[8] else 0.0
                
                precio_aplicable = precio_venta
                descuento_unitario = 0.0
                
                if precio_venta3 > 0 and dcantminpp3 > 0 and cantidad >= dcantminpp3:
                    descuento_unitario = precio_venta - precio_venta3
                    precio_aplicable = precio_venta3
                elif precio_venta2 > 0 and dcantminpp2 > 0 and cantidad >= dcantminpp2:
                    descuento_unitario = precio_venta - precio_venta2
                    precio_aplicable = precio_venta2
                
                subtotal_prod = cantidad * precio_aplicable
                descuento_prod = cantidad * descuento_unitario
                importe_original = cantidad * precio_venta
                
                productos.append({
                    "codigo_barras": codigo_barras,
                    "nombre": nombre_producto,
                    "cantidad": cantidad,
                    "precio_unitario": precio_aplicable,
                    "subtotal": subtotal_prod,
                    "importe_original": importe_original,
                    "unidad": unidad_correcta
                })
                
                subtotal += importe_original
                descuento_total += descuento_prod
            else:
                precio = float(prod.precio)
                subtotal_prod = cantidad * precio
                productos.append({
                    "codigo_barras": codigo_barras,
                    "nombre": prod.nombre,
                    "cantidad": cantidad,
                    "precio_unitario": precio,
                    "subtotal": subtotal_prod,
                    "importe_original": subtotal_prod,
                    "unidad": "PZA"
                })
                subtotal += subtotal_prod
        
        total = subtotal - descuento_total
        
        hoy = datetime.now()
        fecha_vencimiento = (hoy + timedelta(days=30)).strftime("%Y-%m-%d")
        creado_en = hoy.strftime("%Y-%m-%d %H:%M:%S")
        
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
            "observaciones": request.observaciones,
            "fecha_vencimiento": fecha_vencimiento,
            "creado_en": creado_en
        }
        
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
            descuento_total,
            total,
            uuid_cliente,
            uuid_sucursal,
            uuid_cotizacion,
            1
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return {"folio": folio, "uuid_cotizacion": uuid_cotizacion}
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al guardar cotización: {str(e)}")

@app.post("/api/cliente/monedero")
def registrar_cliente(request: ClienteMonederoRequest):
    """Registrar un nuevo cliente en el sistema de monedero"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Validar que el teléfono no exista
        cursor.execute("SELECT idcliente FROM cliente WHERE telefono = %s AND is_active=1 LIMIT 1", (request.telefono,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El teléfono ya está registrado")
        
        # Separar nombre y apellidos
        import re
        partes = re.split(r'\s+', request.nombre_completo.strip())
        if len(partes) == 1:
            nombre = partes[0]
            apellidos = ''
        elif len(partes) == 2:
            nombre, apellidos = partes
        else:
            nombre = partes[0]
            apellidos = ' '.join(partes[1:])
        
        uuid_cliente = str(uuid.uuid4())
        sql = (
            "INSERT INTO cliente (uuid_cliente, nombre, apellidos, razon_social, telefono, puntos, is_active) "
            "VALUES (%s, %s, %s, %s, %s, 0, 1)"
        )
        razon_social = request.nombre_completo.strip()
        cursor.execute(sql, (uuid_cliente, nombre, apellidos, razon_social, request.telefono))
        idcliente = cursor.lastrowid
        
        vCodigoCliente = f"CLI{idcliente:05d}"
        cursor.execute("UPDATE cliente SET vCodigoCliente = %s WHERE idcliente = %s", (vCodigoCliente, idcliente))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'idcliente': idcliente,
            'vCodigoCliente': vCodigoCliente,
            'nombre': nombre,
            'apellidos': apellidos
        }
    except HTTPException:
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al registrar cliente: {str(e)}")

@app.get("/api/cliente/puntos")
def consultar_puntos(busqueda: str):
    """Consultar puntos de un cliente por teléfono, código o ID"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = (
            "SELECT nombre, apellidos, puntos, vCodigoCliente FROM cliente "
            "WHERE is_active=1 AND (idcliente = %s OR telefono = %s OR vCodigoCliente = %s) LIMIT 1"
        )
        cursor.execute(query, (busqueda, busqueda, busqueda))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return {
            "nombre": row.get('nombre', ''),
            "apellidos": row.get('apellidos', ''),
            "puntos": row.get('puntos', 0),
            "vCodigoCliente": row.get('vCodigoCliente', '')
        }
    except HTTPException:
        conn.close()
        raise
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al consultar puntos: {str(e)}")

@app.post("/api/pedido")
def guardar_pedido(request: PedidoRequest):
    """Guardar un pedido y sus detalles"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Insertar cabecera del pedido
        sql_pedido = """
            INSERT INTO pedido (nombre, direccion, colonia, telefono, numero_cliente, pago)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_pedido, (
            request.nombre, request.direccion, request.colonia,
            request.telefono, request.numero_cliente, request.pago
        ))
        pedido_id = cursor.lastrowid
        
        # Insertar productos del pedido
        for prod in request.carrito:
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
                prod.cantidad,
                prod.precio,
                prod.nombre
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"pedido_id": pedido_id}
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al guardar pedido: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # La API se ejecutará en puerto 8001 para no conflictuar con otras APIs
    # Puedes cambiar el puerto si lo necesitas
    uvicorn.run(app, host="0.0.0.0", port=8001)
