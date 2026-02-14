from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from email.mime.text import MIMEText
from datetime import datetime, timezone
from unidecode import unidecode
from collections import defaultdict
from werkzeug.utils import secure_filename
from functools import wraps
from dotenv import load_dotenv
import smtplib
import pandas as pd
from db_config import get_db_connection, obtener_productos_sucursal, guardar_pedido_db, contar_productos_sucursal, contar_productos_sucursal
from routes_imagenes import imagenes_bp
import json
import os
import csv
import shutil
import secrets
import pytz
import requests
import base64

# Cargar variables de entorno desde .env
load_dotenv()

# Zona horaria de México
mexico_timezone = pytz.timezone('America/Mexico_City')

# Archivo local para recuperar pedidos cuando se pierde la sesión (Mercado Pago)
ORDERS_CACHE_FILE = "pedidos_cache.json"


def _load_orders_cache():
    if not os.path.exists(ORDERS_CACHE_FILE):
        return {"orders": {}, "mp_preference_map": {}}
    try:
        with open(ORDERS_CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "orders" not in data:
            data["orders"] = {}
        if "mp_preference_map" not in data:
            data["mp_preference_map"] = {}
        return data
    except Exception as e:
        print(f"❌ Error al leer cache de pedidos: {e}")
        return {"orders": {}, "mp_preference_map": {}}


def _save_orders_cache(data):
    try:
        with open(ORDERS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error al guardar cache de pedidos: {e}")


def _store_order_snapshot(folio, snapshot):
    if not folio:
        return
    data = _load_orders_cache()
    data["orders"][str(folio)] = snapshot
    _save_orders_cache(data)


def _map_preference_to_folio(preference_id, folio):
    if not preference_id or not folio:
        return
    data = _load_orders_cache()
    data["mp_preference_map"][str(preference_id)] = str(folio)
    _save_orders_cache(data)


def _get_order_snapshot_by_folio(folio):
    data = _load_orders_cache()
    return data.get("orders", {}).get(str(folio))


def _get_folio_by_preference_id(preference_id):
    data = _load_orders_cache()
    return data.get("mp_preference_map", {}).get(str(preference_id))



import os
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'cambia_esto_en_produccion')  # Usa variable de entorno

# Habilitar compresión gzip para respuestas más rápidas
try:
    from flask_compress import Compress
    Compress(app)
    print("✅ Compresión gzip habilitada")
except ImportError:
    print("⚠️ flask-compress no instalado, sin compresión gzip")

# Registrar blueprints
app.register_blueprint(imagenes_bp)

# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Caché de 1 año para archivos estáticos

# Asegurar que la carpeta de upload existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Credenciales de administrador (usa variables de entorno en producción)
ADMIN_CREDENTIALS = {
    'admin': os.environ.get('ADMIN_PASSWORD', ''),
    'manager': os.environ.get('MANAGER_PASSWORD', '')
}




def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    return unidecode(texto.strip().lower())

# Función para verificar si una extensión de archivo está permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorador para requerir autenticación en rutas administrativas
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/')
def index():
    plantilla = 'base_movil.html' if es_movil() else 'base_escritorio.html'
    query = request.args.get("q", "")
    departamento = request.args.get("departamento", "")
    categoria = request.args.get("categoria", "")
    orden = request.args.get("orden", "")
    pagina = int(request.args.get('pagina', 1))
    
    # DEBUG: Ver qué parámetros llegan
    print(f"🔍 DEBUG - Parámetros recibidos:")
    print(f"   departamento: '{departamento}'")
    print(f"   categoria: '{categoria}'")
    print(f"   query: '{query}'")
    
    # Paginación solo para escritorio (tanto página principal como ofertas)
    es_desktop = not es_movil()
    por_pagina = 20 if es_desktop else None

    productos = obtener_productos_sucursal(
        departamento=departamento if departamento else None,
        categoria=categoria if categoria else None,
        query=query if query else None,
        orden=orden if orden else None,
        pagina=pagina,
        por_pagina=por_pagina
    )
    
    # Datos para paginación (solo para escritorio)
    total_productos = 0
    total_paginas = 0
    if es_desktop:
        total_productos = contar_productos_sucursal(
            departamento=departamento if departamento else None,
            categoria=categoria if categoria else None,
            query=query if query else None
        )
        total_paginas = (total_productos + por_pagina - 1) // por_pagina

    # Obtener departamentos y categorías únicos desde la base de datos
    from db_config import obtener_departamentos, obtener_categorias
    try:
        departamentos = obtener_departamentos()
    except Exception as e:
        print(f"❌ Error al obtener departamentos: {e}")
        departamentos = []
    
    categorias = []
    if departamento:
        try:
            categorias = obtener_categorias(departamento)
        except Exception as e:
            print(f"❌ Error al obtener categorías: {e}")
            categorias = []

    # Agrupar productos por departamento
    productos_por_departamento = defaultdict(list)
    for p in productos:
        try:
            dep = p['nombre_departamento'] if p['nombre_departamento'] else 'Sin departamento'
        except (KeyError, TypeError):
            dep = 'Sin departamento'
        productos_por_departamento[dep].append(p)

    return render_template("index.html",
                    base_template=plantilla,
                    productos=productos,
                    productos_por_departamento=productos_por_departamento,
                    query=query,
                    departamento=departamento,
                    categoria=categoria,
                    orden=orden,
                    departamentos=departamentos,
                    categorias=categorias,
                    categoria_actual=categoria,
                    query_actual=query,
                    orden_actual=orden,
                    pagina_actual=pagina,
                    total_paginas=total_paginas,
                    total_productos=total_productos,
                    es_desktop=es_desktop)

@app.route('/productos')
def productos():
    # Redirigir a la página principal con los mismos parámetros
    return index()

@app.route('/cart')
def ver_carrito():
    plantilla_base = 'base_movil.html' if es_movil() else 'base_escritorio.html'
    return render_template('cart.html', base_template=plantilla_base)

@app.route('/admin')
def admin_redirect():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "GET":
        plantilla_base = 'base_movil.html' if es_movil() else 'base_escritorio.html'
        mp_error = request.args.get("mp_error", "")
        return render_template("checkout.html", base_template=plantilla_base, mp_error=mp_error)
    else:
        plantilla_base = 'base_movil.html' if es_movil() else 'base_escritorio.html'
        try:
            # Datos enviados por formulario
            nombre = request.form.get("nombre")
            direccion = request.form.get("direccion")
            telefono = request.form.get("telefono")
            numero_cliente = request.form.get("numero_cliente", "").strip()
            pago = request.form.get("pago")
            carrito_json = request.form.get("carrito_json")
            carrito = json.loads(carrito_json)
            colonia = request.form.get("colonia")
            
            # Nuevos campos del formulario mejorado
            horario_entrega = request.form.get("horario_entrega", "")
            pago_efectivo_cambio = request.form.get("pago_efectivo_cambio", "")
            pago_efectivo_monto = request.form.get("pago_efectivo_monto", "")
            
            # Construir información detallada de pago
            info_pago = pago
            if pago == "Efectivo":
                if pago_efectivo_cambio == "si" and pago_efectivo_monto:
                    info_pago = f"Efectivo - Paga con ${pago_efectivo_monto} (necesita cambio)"
                else:
                    info_pago = "Efectivo - Pago justo"
            elif pago == "Tarjeta":
                info_pago = "Tarjeta (repartidor lleva terminal)"
            elif pago == "Transferencia":
                info_pago = "Transferencia SPEI"
            elif pago == "Mercado Pago":
                info_pago = "Mercado Pago (pago en línea)"
            elif pago == "Clip":
                info_pago = "Clip (pago en línea)"
            
            session["colonia"] = colonia
            session["horario_entrega"] = horario_entrega
            session["info_pago"] = info_pago
            session["pago_efectivo_cambio"] = pago_efectivo_cambio
            session["pago_efectivo_monto"] = pago_efectivo_monto


            # Calculamos totales
            total = sum(p["precio"] * p["cantidad"] for p in carrito)
            ahorro = sum((p["precio_original"] - p["precio"]) * p["cantidad"]
                         for p in carrito if p["precio_original"] > p["precio"])

            # Guardamos en sesión
            session["nombre"] = nombre
            session["direccion"] = direccion
            session["telefono"] = telefono
            session["numero_cliente"] = numero_cliente
            session["pago"] = pago
            session["carrito"] = carrito
            session["total"] = total
            session["ahorro"] = ahorro

            # Guardar pedido como cotización en la base de datos
            from db_config import guardar_cotizacion_web
            folio, uuid_cotizacion = guardar_cotizacion_web(carrito)
            session["folio"] = folio
            session["uuid_cotizacion"] = uuid_cotizacion

            snapshot = {
                "nombre": nombre,
                "direccion": direccion,
                "colonia": colonia,
                "telefono": telefono,
                "numero_cliente": numero_cliente,
                "horario_entrega": horario_entrega,
                "pago": pago,
                "info_pago": info_pago,
                "pago_efectivo_cambio": pago_efectivo_cambio,
                "pago_efectivo_monto": pago_efectivo_monto,
                "carrito": carrito,
                "total": total,
                "ahorro": ahorro,
                "folio": folio,
                "created_at": datetime.now(mexico_timezone).strftime('%d/%m/%Y %H:%M')
            }
            _store_order_snapshot(folio, snapshot)

            # Si el método es Mercado Pago, crear preferencia y redirigir
            if pago == "Mercado Pago":
                access_token = os.environ.get("MERCADOPAGO_ACCESS_TOKEN") or os.environ.get("MP_ACCESS_TOKEN")
                if not access_token:
                    return render_template(
                        "checkout.html",
                        base_template=plantilla_base,
                        mp_error="No hay token de Mercado Pago configurado."
                    )

                items = []
                for p in carrito:
                    items.append({
                        "title": p.get("nombre", "Producto"),
                        "quantity": int(p.get("cantidad", 1)),
                        "unit_price": float(p.get("precio", 0)),
                        "currency_id": "MXN"
                    })

                base_url = os.environ.get("PUBLIC_BASE_URL") or request.url_root.rstrip("/")
                if not base_url.startswith("https://"):
                    return render_template(
                        "checkout.html",
                        base_template=plantilla_base,
                        mp_error="Mercado Pago requiere una URL pública https. Configura PUBLIC_BASE_URL con tu dominio https (o ngrok https)."
                    )

                preference = {
                    "items": items,
                    "external_reference": folio or "",
                    "back_urls": {
                        "success": f"{base_url}/confirmacion?status=approved",
                        "pending": f"{base_url}/confirmacion?status=pending",
                        "failure": f"{base_url}/confirmacion?status=failure"
                    },
                    "auto_return": "approved",
                    "payer": {
                        "name": nombre,
                        "phone": {
                            "number": telefono
                        }
                    }
                }

                mp_url = "https://api.mercadopago.com/checkout/preferences"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                response = requests.post(mp_url, headers=headers, json=preference, timeout=20)
                if response.status_code >= 400:
                    print(f"❌ Error Mercado Pago: {response.status_code} - {response.text}")
                    return render_template(
                        "checkout.html",
                        base_template=plantilla_base,
                        mp_error="No se pudo iniciar el pago con Mercado Pago."
                    )

                data = response.json()
                init_point = data.get("init_point")
                if not init_point:
                    print(f"❌ Respuesta Mercado Pago sin init_point: {data}")
                    return render_template(
                        "checkout.html",
                        base_template=plantilla_base,
                        mp_error="No se pudo iniciar el pago con Mercado Pago."
                    )

                session["mp_preference_id"] = data.get("id", "")
                _map_preference_to_folio(session.get("mp_preference_id"), folio)
                return redirect(init_point)

            # Si el método es Clip, crear link de pago y redirigir
            if pago == "Clip":
                clip_api_key = os.environ.get("CLIP_API_KEY")
                clip_api_secret = os.environ.get("CLIP_API_SECRET")
                if not clip_api_key or not clip_api_secret:
                    return render_template(
                        "checkout.html",
                        base_template=plantilla_base,
                        mp_error="No hay credenciales de Clip configuradas (CLIP_API_KEY y CLIP_API_SECRET)."
                    )

                base_url = os.environ.get("PUBLIC_BASE_URL") or request.url_root.rstrip("/")
                if not base_url.startswith("https://"):
                    return render_template(
                        "checkout.html",
                        base_template=plantilla_base,
                        mp_error="Clip requiere una URL pública https. Configura PUBLIC_BASE_URL con tu dominio https."
                    )

                # Generar token Basic Auth: base64(api_key:api_secret)
                clip_credentials = base64.b64encode(f"{clip_api_key}:{clip_api_secret}".encode()).decode()

                clip_payload = {
                    "amount": float(total),
                    "currency": "MXN",
                    "purchase_description": f"Pedido Abarrotes Soto #{folio or 'SN'}",
                    "image_url": f"{base_url}/static/images/logo_abarrotes_soto.png",
                    "redirection_url": {
                        "success": f"{base_url}/confirmacion?clip_status=approved&clip_folio={folio}",
                        "error": f"{base_url}/confirmacion?clip_status=rejected&clip_folio={folio}",
                        "default": f"{base_url}/confirmacion?clip_status=pending&clip_folio={folio}"
                    },
                    "metadata": {
                        "me_reference_id": folio or "",
                        "customer_info": {
                            "name": nombre or "Cliente",
                            "phone": telefono or ""
                        }
                    },
                    "override_settings": {
                        "payment_method": ["card"]
                    }
                }

                clip_url = "https://api.payclip.com/v2/checkout"
                clip_headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {clip_credentials}"
                }

                try:
                    clip_response = requests.post(clip_url, headers=clip_headers, json=clip_payload, timeout=20)
                    if clip_response.status_code >= 400:
                        print(f"❌ Error Clip: {clip_response.status_code} - {clip_response.text}")
                        return render_template(
                            "checkout.html",
                            base_template=plantilla_base,
                            mp_error=f"No se pudo iniciar el pago con Clip. Error: {clip_response.status_code}"
                        )

                    clip_data = clip_response.json()
                    payment_url = clip_data.get("payment_request_url")
                    payment_request_id = clip_data.get("payment_request_id", "")

                    if not payment_url:
                        print(f"❌ Respuesta Clip sin payment_request_url: {clip_data}")
                        return render_template(
                            "checkout.html",
                            base_template=plantilla_base,
                            mp_error="No se pudo obtener el link de pago de Clip."
                        )

                    session["clip_payment_request_id"] = payment_request_id
                    # Mapear el payment_request_id al folio para recuperación
                    _map_preference_to_folio(f"clip_{payment_request_id}", folio)
                    return redirect(payment_url)

                except requests.exceptions.Timeout:
                    return render_template(
                        "checkout.html",
                        base_template=plantilla_base,
                        mp_error="Tiempo de espera agotado al conectar con Clip. Intenta de nuevo."
                    )
                except Exception as clip_err:
                    print(f"❌ Error inesperado Clip: {clip_err}")
                    return render_template(
                        "checkout.html",
                        base_template=plantilla_base,
                        mp_error="Error inesperado al procesar pago con Clip."
                    )

            return redirect("/confirmacion")

        except Exception as e:
            print("❌ Error al procesar pedido:", e)
            return jsonify({"error": "Error al procesar el pedido"}), 500


@app.route("/monedero", methods=["GET", "POST"])
def monedero():
    plantilla_base = 'base_movil.html' if es_movil() else 'base_escritorio.html'


    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        from db_config import registrar_cliente_monedero
        resultado, error = registrar_cliente_monedero(nombre, telefono)
        if error:
            mensaje = f"❌ {error}"
            return render_template("monedero.html", mensaje=mensaje, base_template=plantilla_base)
        else:
            numero_cliente = resultado['vCodigoCliente']
            # enviar_correo(nombre, telefono, numero_cliente)  # Opcional: descomentar si se requiere
            print(f"Registrado: {numero_cliente} - {nombre} - {telefono}")
            mensaje = f"✅ Cliente registrado correctamente. Tu número de cliente es: {numero_cliente}"
            return render_template("monedero.html", mensaje=mensaje, base_template=plantilla_base)

    return render_template("monedero.html", mensaje=None, base_template=plantilla_base)


def enviar_correo(nombre, telefono, cliente_id):
    remitente = "sotojaimes98@gmail.com"
    destinatario = "sotojaimes98@gmail.com"
    asunto = f"Nuevo cliente registrado: {cliente_id}"
    cuerpo = f"""
🧾 Nuevo registro:

🆔 Cliente: {cliente_id}
👤 Nombre: {nombre}
📞 Teléfono: {telefono}
    """

    msg = MIMEText(cuerpo)
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remitente, "peev aiuu kevv qpqe")  # tu contraseña de app
            servidor.send_message(msg)
            print("✅ Correo enviado correctamente.")
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")


def generar_numero_cliente():
    archivo = "clientes.csv"
    ultimo_id = 0

    if os.path.exists(archivo):
        with open(archivo, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            filas = list(reader)
            if len(filas) > 1:  # hay datos
                ultimo_id = int(filas[-1][0][3:])  # extrae número de cliente (ej. 0001)

    nuevo_id = ultimo_id + 1
    numero_cliente = f"502{nuevo_id:04d}"
    return numero_cliente


@app.route("/rifa2026")
def rifa2026():
    """Página dedicada a la RIFA 2026 con toda la información"""
    return render_template("rifa2026.html")


@app.route("/confirmacion")
def confirmacion():
    nombre = session.get("nombre", "")
    direccion = session.get("direccion", "")
    colonia = session.get("colonia", "")
    telefono = session.get("telefono", "")
    numero_cliente = session.get("numero_cliente", "")
    pago = session.get("pago", "")
    info_pago = session.get("info_pago", pago)  # Información detallada del pago
    horario_entrega = session.get("horario_entrega", "")
    pago_efectivo_cambio = session.get("pago_efectivo_cambio", "")
    pago_efectivo_monto = session.get("pago_efectivo_monto", "")
    carrito = session.get("carrito", [])
    total = session.get("total", 0)
    ahorro = session.get("ahorro", 0)
    folio = session.get("folio", "")

    # Detectar retorno de Mercado Pago y ajustar método de pago si aplica
    mp_status = request.args.get("collection_status") or request.args.get("status")
    mp_payment_id = request.args.get("payment_id") or request.args.get("collection_id")
    mp_preference_id = request.args.get("preference_id")

    # Detectar retorno de Clip
    clip_status = request.args.get("clip_status")
    clip_folio = request.args.get("clip_folio")

    if clip_status:
        pago = "Clip"
        estado_clip = clip_status.lower()
        if estado_clip == "approved":
            info_pago = "Clip (pago en línea aprobado)"
        elif estado_clip == "rejected":
            info_pago = "Clip (pago rechazado)"
        else:
            info_pago = f"Clip (estado: {clip_status})"
        session["pago"] = pago
        session["info_pago"] = info_pago

        # Recuperar datos si la sesión llegó vacía (retorno de Clip)
        datos_vacios_clip = not carrito and not nombre and not direccion and not telefono
        if datos_vacios_clip and clip_folio:
            try:
                snapshot = _get_order_snapshot_by_folio(clip_folio)
                if snapshot:
                    nombre = snapshot.get("nombre", "")
                    direccion = snapshot.get("direccion", "")
                    colonia = snapshot.get("colonia", "")
                    telefono = snapshot.get("telefono", "")
                    numero_cliente = snapshot.get("numero_cliente", "")
                    horario_entrega = snapshot.get("horario_entrega", "")
                    pago_efectivo_cambio = snapshot.get("pago_efectivo_cambio", "")
                    pago_efectivo_monto = snapshot.get("pago_efectivo_monto", "")
                    carrito = snapshot.get("carrito", [])
                    total = snapshot.get("total", 0)
                    ahorro = snapshot.get("ahorro", 0)
                    folio = snapshot.get("folio", clip_folio)

                    session["nombre"] = nombre
                    session["direccion"] = direccion
                    session["colonia"] = colonia
                    session["telefono"] = telefono
                    session["numero_cliente"] = numero_cliente
                    session["horario_entrega"] = horario_entrega
                    session["pago"] = pago
                    session["info_pago"] = info_pago
                    session["carrito"] = carrito
                    session["total"] = total
                    session["ahorro"] = ahorro
                    session["folio"] = folio
            except Exception as e:
                print(f"❌ Error al recuperar datos de Clip: {e}")

        # Consultar estado real del pago en Clip si tenemos el payment_request_id
        clip_payment_request_id = session.get("clip_payment_request_id")
        if clip_payment_request_id:
            try:
                clip_api_key = os.environ.get("CLIP_API_KEY")
                clip_api_secret = os.environ.get("CLIP_API_SECRET")
                if clip_api_key and clip_api_secret:
                    clip_credentials = base64.b64encode(f"{clip_api_key}:{clip_api_secret}".encode()).decode()
                    clip_check_url = f"https://api.payclip.com/v2/checkout/{clip_payment_request_id}"
                    clip_headers = {"Authorization": f"Basic {clip_credentials}"}
                    clip_resp = requests.get(clip_check_url, headers=clip_headers, timeout=15)
                    if clip_resp.status_code < 400:
                        clip_data = clip_resp.json()
                        clip_real_status = clip_data.get("status", "").upper()
                        if clip_real_status == "COMPLETED":
                            info_pago = "Clip (pago en línea aprobado ✅)"
                        elif clip_real_status == "REJECTED":
                            info_pago = "Clip (pago rechazado ❌)"
                        elif clip_real_status == "EXPIRED":
                            info_pago = "Clip (pago expirado)"
                        else:
                            info_pago = f"Clip (estado: {clip_real_status})"
                        session["info_pago"] = info_pago
            except Exception as clip_err:
                print(f"⚠️ No se pudo verificar estado Clip: {clip_err}")

    elif mp_status or mp_payment_id:
        pago = "Mercado Pago"
        if mp_status:
            estado = mp_status.lower()
            if estado == "approved":
                info_pago = "Mercado Pago (pago en línea aprobado)"
            else:
                info_pago = f"Mercado Pago (estado: {mp_status})"
        else:
            info_pago = "Mercado Pago (pago en línea)"
        session["pago"] = pago
        session["info_pago"] = info_pago

    # Recuperar datos si la sesión llegó vacía (retorno de Mercado Pago)
    datos_vacios = not carrito and not nombre and not direccion and not telefono
    if datos_vacios and (mp_payment_id or mp_preference_id):
        try:
            folio_recuperado = None

            # Intentar por preference_id
            if mp_preference_id:
                folio_recuperado = _get_folio_by_preference_id(mp_preference_id)

            # Intentar por payment_id consultando a Mercado Pago
            if not folio_recuperado and mp_payment_id:
                access_token = os.environ.get("MERCADOPAGO_ACCESS_TOKEN") or os.environ.get("MP_ACCESS_TOKEN")
                if access_token:
                    mp_payment_url = f"https://api.mercadopago.com/v1/payments/{mp_payment_id}"
                    headers = {"Authorization": f"Bearer {access_token}"}
                    resp = requests.get(mp_payment_url, headers=headers, timeout=20)
                    if resp.status_code < 400:
                        payment_data = resp.json()
                        folio_recuperado = payment_data.get("external_reference")
                        if not mp_status:
                            mp_status = payment_data.get("status")
                    else:
                        print(f"❌ Error consultando pago MP: {resp.status_code} - {resp.text}")

            # Cargar snapshot desde cache
            if folio_recuperado:
                snapshot = _get_order_snapshot_by_folio(folio_recuperado)
                if snapshot:
                    nombre = snapshot.get("nombre", "")
                    direccion = snapshot.get("direccion", "")
                    colonia = snapshot.get("colonia", "")
                    telefono = snapshot.get("telefono", "")
                    numero_cliente = snapshot.get("numero_cliente", "")
                    horario_entrega = snapshot.get("horario_entrega", "")
                    pago = snapshot.get("pago", pago)
                    info_pago = snapshot.get("info_pago", info_pago)
                    pago_efectivo_cambio = snapshot.get("pago_efectivo_cambio", "")
                    pago_efectivo_monto = snapshot.get("pago_efectivo_monto", "")
                    carrito = snapshot.get("carrito", [])
                    total = snapshot.get("total", 0)
                    ahorro = snapshot.get("ahorro", 0)
                    folio = snapshot.get("folio", folio_recuperado)

                    session["nombre"] = nombre
                    session["direccion"] = direccion
                    session["colonia"] = colonia
                    session["telefono"] = telefono
                    session["numero_cliente"] = numero_cliente
                    session["horario_entrega"] = horario_entrega
                    session["pago"] = pago
                    session["info_pago"] = info_pago
                    session["pago_efectivo_cambio"] = pago_efectivo_cambio
                    session["pago_efectivo_monto"] = pago_efectivo_monto
                    session["carrito"] = carrito
                    session["total"] = total
                    session["ahorro"] = ahorro
                    session["folio"] = folio
        except Exception as e:
            print(f"❌ Error al recuperar datos de MP: {e}")

    plantilla_base = 'base_movil.html' if es_movil() else 'base_escritorio.html'

    # Obtener fecha y hora en formato de México
    fecha_hora_mx = datetime.now(mexico_timezone).strftime('%d/%m/%Y %H:%M')

    # Guardar el pedido en CSV
    try:
        pedido_id = str(int(datetime.now().timestamp()))
        fecha = fecha_hora_mx

        # Crear archivo si no existe
        if not os.path.exists("pedidos.csv"):
            with open("pedidos.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "fecha", "nombre", "direccion", "colonia", "telefono", "metodo_pago", "total", "estado"])

        # Guardar datos del pedido
        with open("pedidos.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([pedido_id, fecha, nombre, direccion, colonia, telefono, pago, total, "Pendiente"])

        # Ya no se guarda el detalle en archivo JSON, ahora se guarda en la base de datos

    except Exception as e:
        print(f"❌ Error al guardar pedido: {e}")

    datos_completos = bool(carrito) and (bool(telefono) or bool(direccion) or bool(nombre))
    telegram_enviado = session.get("telegram_enviado", False)

    # Enviar notificación a Telegram
    try:
        if datos_completos and not telegram_enviado:
            from telegram_notifier import send_telegram_message

            # Crear enlace de WhatsApp
            telefono_limpio = telefono.replace(" ", "").replace("-", "")
            enlace_whatsapp = f"https://wa.me/{telefono_limpio}"

            # Determinar emoji para el horario
            horario_emoji = "🚀" if "antes posible" in horario_entrega.lower() else "⏰"
            
            # Determinar emoji y detalles para el método de pago
            if pago == "Efectivo":
                pago_emoji = "💵"
                # Validar que las variables de efectivo existan antes de usarlas
                efectivo_cambio = pago_efectivo_cambio if 'pago_efectivo_cambio' in locals() else ""
                efectivo_monto = pago_efectivo_monto if 'pago_efectivo_monto' in locals() else ""
                
                if efectivo_cambio == "si" and efectivo_monto:
                    try:
                        monto = float(efectivo_monto)
                        cambio = monto - total
                        pago_detalle = f"Paga con ${monto:.2f} (necesita cambio de ${cambio:.2f})"
                    except (ValueError, TypeError):
                        pago_detalle = "Pago justo (sin cambio)"
                else:
                    pago_detalle = "Pago justo (sin cambio)"
            elif pago == "Tarjeta":
                pago_emoji = "💳"
                pago_detalle = "Repartidor llevará terminal bancaria\n• Acepta débito y crédito\n• Visa, MasterCard, AmEx\n• Sin comisiones"
            elif pago == "Transferencia":
                pago_emoji = "🏦"
                pago_detalle = "SPEI/Transferencia bancaria\n• Tarjeta: 5204 1662 0566 9791\n• Banco: BANAMEX\n• A nombre de: EFREN UZIEL SOTO JAIMES"
            elif pago == "Mercado Pago":
                pago_emoji = "📱"
                if mp_status:
                    pago_detalle = f"Pago en línea con Mercado Pago\n• Estado: {mp_status}"
                else:
                    pago_detalle = "Pago en línea con Mercado Pago"
                if mp_payment_id:
                    pago_detalle += f"\n• ID de pago: {mp_payment_id}"
            elif pago == "Clip":
                pago_emoji = "🔷"
                if clip_status:
                    pago_detalle = f"Pago en línea con Clip\n• Estado: {clip_status}"
                else:
                    pago_detalle = "Pago en línea con Clip"
                clip_req_id = session.get("clip_payment_request_id", "")
                if clip_req_id:
                    pago_detalle += f"\n• ID de pago: {clip_req_id}"
            else:
                pago_emoji = "💰"
                pago_detalle = info_pago

            mensaje = f"""🛒 <b>NUEVO PEDIDO RECIBIDO</b>

👤 <b>DATOS DEL CLIENTE</b>
<b>Nombre:</b> {nombre}
<b>Dirección:</b> {direccion}
<b>Colonia:</b> {colonia}
<b>Teléfono:</b> {telefono}"""

            if numero_cliente:
                mensaje += f"\n<b>N° Cliente:</b> {numero_cliente}"

            mensaje += f"""

{horario_emoji} <b>HORARIO DE ENTREGA</b>
<b>{horario_entrega}</b>

{pago_emoji} <b>MÉTODO DE PAGO</b>
<b>{pago}</b>
{pago_detalle}

📦 <b>PRODUCTOS PEDIDOS</b>"""

            # Agregar productos con mejor formato
            for p in carrito:
                precio_unitario = p['precio']
                cantidad = p['cantidad']
                subtotal = cantidad * precio_unitario
                
                # Mostrar si hay descuento
                if p.get('precio_original') and p['precio_original'] > precio_unitario:
                    descuento = p['precio_original'] - precio_unitario
                    mensaje += f"\n• {p['nombre']}"
                    mensaje += f"\n  📊 {cantidad} x ${precio_unitario:.2f} = <b>${subtotal:.2f}</b>"
                    mensaje += f"\n  💸 Descuento: ${descuento:.2f} c/u"
                else:
                    mensaje += f"\n• {p['nombre']}"
                    mensaje += f"\n  📊 {cantidad} x ${precio_unitario:.2f} = <b>${subtotal:.2f}</b>"

            mensaje += f"""\n\n💰 <b>RESUMEN FINANCIERO</b>"""
            
            if ahorro > 0:
                subtotal_original = total + ahorro
                mensaje += f"\n<b>Subtotal:</b> ${subtotal_original:.2f}"
                mensaje += f"\n<b>Descuentos:</b> -${ahorro:.2f}"
                mensaje += f"\n<b>TOTAL A PAGAR:</b> ${total:.2f} ✅"
            else:
                mensaje += f"\n<b>TOTAL A PAGAR:</b> ${total:.2f} ✅"

            mensaje += f"""\n\n📅 <b>INFORMACIÓN ADICIONAL</b>
<b>Fecha/Hora:</b> {fecha_hora_mx}
<b>Folio:</b> #{folio if folio else 'N/A'}"""

            # Agregar enlace de WhatsApp con mejor formato
            mensaje += f"""\n\n📱 <b>CONTACTO DIRECTO</b>
<a href="{enlace_whatsapp}">💬 Abrir chat de WhatsApp</a>

🚛 <i>Procesando pedido para entrega...</i>"""

            send_telegram_message(mensaje)
            session["telegram_enviado"] = True

    except Exception as e:
        print(f"❌ Error al enviar notificación a Telegram: {e}")

    return render_template("confirmacion.html",
                           base_template=plantilla_base,
                           nombre=nombre or "Cliente",
                           direccion=direccion,
                           colonia=colonia,
                           telefono=telefono,
                           numero_cliente=numero_cliente,
                           pago=pago,
                           info_pago=info_pago,
                           horario_entrega=horario_entrega,
                           carrito=carrito,
                           total=total,
                           ahorro=ahorro,
                           pedido_id=session.get("folio"),
                           mp_status=mp_status,
                           mp_payment_id=mp_payment_id,
                           clip_status=clip_status)


@app.route("/api/confirmacion/recuperar", methods=["POST"])
def recuperar_confirmacion():
    try:
        data = request.get_json(silent=True) or {}

        nombre = (data.get("nombre") or "").strip()
        direccion = (data.get("direccion") or "").strip()
        colonia = (data.get("colonia") or "").strip()
        telefono = (data.get("telefono") or "").strip()
        numero_cliente = (data.get("numero_cliente") or "").strip()
        horario_entrega = (data.get("horario_entrega") or "").strip()
        pago = (data.get("pago") or "").strip()
        info_pago = (data.get("info_pago") or pago).strip()
        pago_efectivo_cambio = (data.get("pago_efectivo_cambio") or "").strip()
        pago_efectivo_monto = (data.get("pago_efectivo_monto") or "").strip()
        carrito = data.get("carrito") or []
        folio = (data.get("folio") or "").strip()

        if not isinstance(carrito, list):
            carrito = []

        if not data.get("total"):
            total = sum(float(p.get("precio", 0)) * int(p.get("cantidad", 0)) for p in carrito)
        else:
            total = float(data.get("total", 0))

        if not data.get("ahorro"):
            ahorro = sum(
                (float(p.get("precio_original", 0)) - float(p.get("precio", 0))) * int(p.get("cantidad", 0))
                for p in carrito
                if float(p.get("precio_original", 0)) > float(p.get("precio", 0))
            )
        else:
            ahorro = float(data.get("ahorro", 0))

        session["nombre"] = nombre
        session["direccion"] = direccion
        session["colonia"] = colonia
        session["telefono"] = telefono
        session["numero_cliente"] = numero_cliente
        session["horario_entrega"] = horario_entrega
        session["pago"] = pago
        session["info_pago"] = info_pago
        session["pago_efectivo_cambio"] = pago_efectivo_cambio
        session["pago_efectivo_monto"] = pago_efectivo_monto
        session["carrito"] = carrito
        session["total"] = total
        session["ahorro"] = ahorro
        if folio:
            session["folio"] = folio

        session["telegram_enviado"] = False

        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al recuperar confirmación: {e}")
        return jsonify({"success": False, "error": "Error al recuperar confirmación"}), 500


def es_movil():
    agente = request.user_agent.string.lower()
    return any(x in agente for x in ['iphone', 'android', 'blackberry', 'windows phone'])


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Credenciales incorrectas')

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Obtener estadísticas desde la BD azula_pdv
    from db_config import obtener_estadisticas_admin, obtener_productos_bajo_stock
    try:
        stats = obtener_estadisticas_admin()
        productos_bajo_stock = obtener_productos_bajo_stock(5)

        # Formatear últimos pedidos para la plantilla
        ultimos_pedidos = []
        for p in stats.get('ultimos_pedidos', []):
            ultimos_pedidos.append({
                "cliente": p.get('nombre', 'N/A'),
                "fecha": p.get('fecha', ''),
                "total": str(p.get('total', 0)),
                "estado": p.get('estado', 'Pendiente')
            })

        return render_template('admin.html',
                               total_productos=stats['total_productos'],
                               total_clientes=stats['total_clientes'],
                               pedidos_pendientes=stats['pedidos_pendientes'],
                               ventas_mes=f"{stats['ventas_mes']:.2f}",
                               productos_bajo_stock=productos_bajo_stock,
                               ultimos_pedidos=ultimos_pedidos)
    except Exception as e:
        print(f"❌ Error en dashboard: {e}")
        return render_template('admin.html',
                               total_productos=0, total_clientes=0,
                               pedidos_pendientes=0, ventas_mes="0.00",
                               productos_bajo_stock=[], ultimos_pedidos=[])

@app.route('/admin/productos')
@admin_required
def admin_productos():
    from db_config import obtener_todos_productos_admin, obtener_departamentos, obtener_categorias
    pagina_actual = int(request.args.get('pagina', 1))
    productos_por_pagina = 50

    productos_pagina, total_productos = obtener_todos_productos_admin(pagina_actual, productos_por_pagina)
    total_paginas = (total_productos + productos_por_pagina - 1) // productos_por_pagina

    categorias = obtener_categorias()
    departamentos = obtener_departamentos()

    return render_template('admin_productos.html',
                           productos=productos_pagina,
                           categorias=categorias,
                           departamentos=departamentos,
                           pagina_actual=pagina_actual,
                           total_paginas=total_paginas)

@app.route('/admin/productos/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_producto_nuevo():
    from db_config import obtener_departamentos, obtener_categorias, crear_producto_db
    categorias = obtener_categorias()
    departamentos = obtener_departamentos()

    if request.method == 'POST':
        try:
            cbarras = request.form.get('cbarras')
            nombre_producto = request.form.get('nombre_producto')

            # Manejo de categoría
            if request.form.get('nombre_categoria') == 'nueva':
                nombre_categoria = request.form.get('nueva_categoria')
            else:
                nombre_categoria = request.form.get('nombre_categoria')

            # Manejo de departamento
            if request.form.get('nombre_dep') == 'nuevo':
                nombre_dep = request.form.get('nuevo_departamento')
            else:
                nombre_dep = request.form.get('nombre_dep')

            precio_venta = float(request.form.get('precio_venta'))
            precio_venta2 = request.form.get('precio_venta2')
            precio_venta2 = float(precio_venta2) if precio_venta2 else 0.0
            existencia = int(float(request.form.get('existencia')))

            # Manejar imagen
            imagen_filename = None
            if 'imagen' in request.files and request.files['imagen'].filename:
                imagen = request.files['imagen']
                if allowed_file(imagen.filename):
                    extension = os.path.splitext(imagen.filename)[1]
                    imagen_filename = f"{cbarras}{extension}"
                    imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
                    if os.path.exists(imagen_path):
                        try:
                            os.remove(imagen_path)
                        except Exception as e:
                            print(f"Error al eliminar imagen previa: {e}")
                    imagen.save(imagen_path)

            datos = {
                'cbarras': cbarras,
                'nombre_producto': nombre_producto,
                'nombre_categoria': nombre_categoria,
                'nombre_dep': nombre_dep,
                'precio_venta': precio_venta,
                'precio_venta2': precio_venta2,
                'existencia': existencia,
                'imagen': imagen_filename
            }

            producto_id, error = crear_producto_db(datos)
            if error:
                return render_template('admin_producto_form.html',
                                       error=True, mensaje=error,
                                       producto=None,
                                       categorias=categorias,
                                       departamentos=departamentos)

            return redirect(url_for('admin_productos'))

        except Exception as e:
            return render_template('admin_producto_form.html',
                                   error=True,
                                   mensaje=f"Error al crear producto: {str(e)}",
                                   producto=None,
                                   categorias=categorias,
                                   departamentos=departamentos)

    return render_template('admin_producto_form.html',
                           producto=None,
                           categorias=categorias,
                           departamentos=departamentos)

@app.route('/admin/productos/editar/<cbarras>', methods=['GET', 'POST'])
@admin_required
def admin_producto_editar(cbarras):
    from db_config import obtener_producto_por_codigo, obtener_departamentos, obtener_categorias, actualizar_producto_db

    producto = obtener_producto_por_codigo(cbarras)
    if not producto:
        return redirect(url_for('admin_productos'))

    categorias = obtener_categorias()
    departamentos = obtener_departamentos()

    if request.method == 'POST':
        try:
            nombre_producto = request.form.get('nombre_producto')

            if request.form.get('nombre_categoria') == 'nueva':
                nombre_categoria = request.form.get('nueva_categoria')
            else:
                nombre_categoria = request.form.get('nombre_categoria')

            if request.form.get('nombre_dep') == 'nuevo':
                nombre_dep = request.form.get('nuevo_departamento')
            else:
                nombre_dep = request.form.get('nombre_dep')

            precio_venta = float(request.form.get('precio_venta'))
            precio_venta2 = request.form.get('precio_venta2')
            precio_venta2 = float(precio_venta2) if precio_venta2 and precio_venta2.strip() else 0.0
            existencia = int(float(request.form.get('existencia')))

            # Manejar imagen
            imagen_filename = None
            if 'imagen' in request.files and request.files['imagen'].filename:
                imagen = request.files['imagen']
                if allowed_file(imagen.filename):
                    extension = os.path.splitext(imagen.filename)[1]
                    imagen_filename = f"{cbarras}{extension}"
                    imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
                    if os.path.exists(imagen_path):
                        try:
                            os.remove(imagen_path)
                        except Exception as e:
                            print(f"Error al eliminar imagen previa: {e}")
                    imagen.save(imagen_path)

            datos = {
                'nombre_producto': nombre_producto,
                'nombre_categoria': nombre_categoria,
                'nombre_dep': nombre_dep,
                'precio_venta': precio_venta,
                'precio_venta2': precio_venta2,
                'existencia': existencia,
                'imagen': imagen_filename
            }

            ok, error = actualizar_producto_db(cbarras, datos)
            if not ok:
                return render_template('admin_producto_form.html',
                                       error=True, mensaje=error,
                                       producto=producto,
                                       categorias=categorias,
                                       departamentos=departamentos)

            return redirect(url_for('admin_productos'))

        except Exception as e:
            return render_template('admin_producto_form.html',
                                   error=True,
                                   mensaje=f"Error al actualizar producto: {str(e)}",
                                   producto=producto,
                                   categorias=categorias,
                                   departamentos=departamentos)

    return render_template('admin_producto_form.html',
                           producto=producto,
                           categorias=categorias,
                           departamentos=departamentos)

@app.route('/admin/productos/eliminar/<cbarras>')
@admin_required
def admin_producto_eliminar(cbarras):
    from db_config import eliminar_producto_db
    eliminar_producto_db(cbarras)
    return redirect(url_for('admin_productos'))

@app.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    from db_config import obtener_pedidos_admin
    try:
        pedidos = obtener_pedidos_admin()
    except Exception as e:
        print(f"❌ Error obteniendo pedidos: {e}")
        pedidos = []
    return render_template('admin_pedidos.html', pedidos=pedidos)

@app.route('/admin/pedidos/detalle/<pedido_id>')
@admin_required
def admin_pedido_detalle(pedido_id):
    # Buscar detalles del pedido en la BD
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM pedidos_online WHERE id = %s OR numero_pedido = %s LIMIT 1
        """, (pedido_id, pedido_id))
        pedido_info = cursor.fetchone()

        if not pedido_info:
            flash("No se encontró el detalle del pedido")
            cursor.close()
            conn.close()
            return redirect(url_for('admin_pedidos'))

        cursor.execute("""
            SELECT nombre_producto, cantidad, precio_unitario, descuento, subtotal
            FROM detalles_pedido_online WHERE pedido_id = %s
        """, (pedido_info['id'],))
        detalles = cursor.fetchall()
        cursor.close()
        conn.close()

        pedido = {
            "cliente": {
                "nombre": pedido_info.get('cliente_nombre', 'N/A'),
                "telefono": pedido_info.get('cliente_telefono', ''),
                "direccion": pedido_info.get('direccion', ''),
            },
            "total": float(pedido_info.get('total', 0)),
            "estado": pedido_info.get('estado', 'Pendiente'),
            "metodo_pago": pedido_info.get('metodo_pago', ''),
            "productos": detalles
        }
        return render_template('admin_pedido_detalle.html', pedido=pedido)
    except Exception as e:
        print(f"Error obteniendo detalle pedido: {e}")
        flash("Error al obtener detalle del pedido")
        return redirect(url_for('admin_pedidos'))

@app.route('/admin/pedidos/estado/<pedido_id>/<nuevo_estado>')
@admin_required
def admin_pedido_estado(pedido_id, nuevo_estado):
    estados_validos = ["Pendiente", "En proceso", "Enviado", "Entregado", "Cancelado"]
    if nuevo_estado not in estados_validos:
        flash("Estado no válido")
        return redirect(url_for('admin_pedidos'))

    from db_config import actualizar_estado_pedido
    actualizar_estado_pedido(pedido_id, nuevo_estado)

    flash(f"Estado del pedido actualizado a {nuevo_estado}")
    return redirect(url_for('admin_pedidos'))

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('index'))

# --- CONSULTAR PUNTOS MONEDERO ---
@app.route("/consultar_puntos", methods=["GET", "POST"])
def consultar_puntos():
    puntos = None
    pesos = None
    iniciales = None
    error = None
    nombre_completo = None
    nombre_mascara = None
    if request.method == "POST":
        busqueda = request.form.get("busqueda", "").strip()
        if not busqueda:
            error = "Debes ingresar un teléfono o número de cliente."
        else:
            try:
                from db_config import consultar_puntos_cliente
                row, error = consultar_puntos_cliente(busqueda)
                
                if row:
                    # row es un dict
                    nombre = row.get('nombre', '')
                    apellidos = row.get('apellidos', '')
                    puntos_val = row.get('puntos')
                    
                    # Nombre completo
                    nombre_completo = f"{nombre} {apellidos}".strip()
                    
                    # Máscara tipo M***** S*** J*****
                    def mascarar_parte(parte):
                        parte = parte.strip()
                        if not parte:
                            return ''
                        partes = parte.split()
                        resultado = []
                        for p in partes:
                            if len(p) == 1:
                                resultado.append(p.upper())
                            else:
                                resultado.append(p[0].upper() + '*' * (len(p)-1))
                        return ' '.join(resultado)
                    
                    nombre_mascara = ''
                    if nombre:
                        nombre_mascara += mascarar_parte(nombre)
                    if apellidos:
                        if nombre_mascara:
                            nombre_mascara += ' '
                        nombre_mascara += mascarar_parte(apellidos)
                    
                    # Obtener iniciales
                    iniciales = ''
                    for parte in (nombre, apellidos):
                        if parte and isinstance(parte, str) and parte.strip():
                            iniciales += parte.strip()[0].upper()
                    
                    if puntos_val is not None:
                        if isinstance(puntos_val, (int, float)):
                            puntos = puntos_val
                            pesos = round(float(puntos_val) / 100, 2)
                        elif isinstance(puntos_val, str):
                            try:
                                puntos_float = float(puntos_val)
                                puntos = puntos_float
                                pesos = round(puntos_float / 100, 2)
                            except Exception:
                                puntos = puntos_val
                                pesos = None
                        else:
                            puntos = puntos_val
                            pesos = None
            except Exception as e:
                error = f"Error al consultar: {e}"
    plantilla_base = 'base_movil.html' if es_movil() else 'base_escritorio.html'
    return render_template("consultar_puntos.html", base_template=plantilla_base, puntos=puntos, pesos=pesos, iniciales=iniciales, error=error, nombre_completo=nombre_completo, nombre_mascara=nombre_mascara)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
