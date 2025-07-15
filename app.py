from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from email.mime.text import MIMEText
from flask import session  # ✅ necesario para usar sesiones
from datetime import datetime
from unidecode import unidecode
from collections import defaultdict
from werkzeug.utils import secure_filename
from functools import wraps
import smtplib
import pandas as pd
import json
import os
import csv
import shutil
import secrets


app = Flask(__name__)
app.secret_key = 'mexico'  # puede ser cualquier texto, pero debe estar

# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que la carpeta de upload existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Credenciales de administrador (en un entorno real, usar hashing de contraseñas y almacenamiento seguro)
ADMIN_CREDENTIALS = {
    'admin': 'abarrotessoto2023',
    'manager': 'manager2023'
}

df = pd.read_excel("productos.xlsx")

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

    productos = df[df["existencia"] >= 1].copy()

    if departamento:
        productos = productos[productos["nombre_dep"] == departamento]
    if categoria:
        productos = productos[productos["nombre_categoria"] == categoria]
    if query:
        palabra = normalizar(query)

        productos = productos[productos.apply(lambda p: (
            palabra in normalizar(p["nombre_producto"]) or
            palabra in normalizar(str(p.get("nombre_categoria", ""))) or
            palabra in normalizar(str(p.get("nombre_dep", "")))
        ), axis=1)]

    if orden == "nombre_asc":
        productos = productos.sort_values(by="nombre_producto")
    elif orden == "precio_asc":
        productos["precio_base"] = productos.apply(lambda x: x["precio_venta2"] if x["precio_venta2"] > 0 else x["precio_venta"], axis=1)
        productos = productos.sort_values(by="precio_base")
    elif orden == "precio_desc":
        productos["precio_base"] = productos.apply(lambda x: x["precio_venta2"] if x["precio_venta2"] > 0 else x["precio_venta"], axis=1)
        productos = productos.sort_values(by="precio_base", ascending=False)

    departamentos = sorted(df["nombre_dep"].dropna().unique())
    categorias = sorted(productos["nombre_categoria"].dropna().unique()) if departamento else []

    productos_dict = productos.to_dict(orient="records")

    # Agrupar productos por departamento
    productos_por_departamento = defaultdict(list)
    for p in productos_dict:
        productos_por_departamento[p["nombre_dep"]].append(p)

    return render_template("index.html",
                    base_template=plantilla,
                    productos=productos_dict,
                    productos_por_departamento=productos_por_departamento,
                    query=query,
                    departamento=departamento,
                    categoria=categoria,
                    departamentos=departamentos,
                    categorias=categorias)

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
        return render_template("checkout.html", base_template=plantilla_base)
    else:
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
            session["colonia"] = colonia


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

        numero_cliente = generar_numero_cliente()

        with open("clientes.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["cliente_id", "nombre", "telefono"])
            writer.writerow([numero_cliente, nombre, telefono])

        enviar_correo(nombre, telefono, numero_cliente)
        print(f"Registrado: {numero_cliente} - {nombre} - {telefono}")

        return render_template("monedero.html",
                               mensaje=f"✅ Cliente registrado correctamente. Tu número de cliente es: {numero_cliente}",
                               base_template=plantilla_base)

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


@app.route("/confirmacion")
def confirmacion():
    nombre = session.get("nombre", "Cliente")
    direccion = session.get("direccion", "")
    colonia = session.get("colonia", "")
    telefono = session.get("telefono", "")
    numero_cliente = session.get("numero_cliente", "")
    pago = session.get("pago", "")
    carrito = session.get("carrito", [])
    total = session.get("total", 0)
    ahorro = session.get("ahorro", 0)

    plantilla_base = 'base_movil.html' if es_movil() else 'base_escritorio.html'

    # Guardar el pedido en CSV
    try:
        pedido_id = str(int(datetime.now().timestamp()))
        fecha = datetime.now().strftime('%d/%m/%Y %H:%M')

        # Crear archivo si no existe
        if not os.path.exists("pedidos.csv"):
            with open("pedidos.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "fecha", "nombre", "direccion", "colonia", "telefono", "metodo_pago", "total", "estado"])

        # Guardar datos del pedido
        with open("pedidos.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([pedido_id, fecha, nombre, direccion, colonia, telefono, pago, total, "Pendiente"])

        # Guardar detalle del pedido
        detalle_filename = f"pedido_{pedido_id}_detalle.json"
        with open(detalle_filename, "w", encoding="utf-8") as f:
            json.dump({
                "id": pedido_id,
                "fecha": fecha,
                "cliente": {
                    "nombre": nombre,
                    "direccion": direccion,
                    "colonia": colonia,
                    "telefono": telefono,
                    "numero_cliente": numero_cliente
                },
                "productos": carrito,
                "metodo_pago": pago,
                "total": total,
                "ahorro": ahorro
            }, indent=2)

    except Exception as e:
        print(f"❌ Error al guardar pedido: {e}")

    # Enviar notificación a Telegram
    try:
        from telegram_notifier import send_telegram_message

        mensaje = f"""<b>🛒 NUEVO PEDIDO</b>\n\n
<b>Cliente:</b> {nombre}
<b>Dirección:</b> {direccion}
<b>Colonia:</b> {colonia}
<b>Teléfono:</b> {telefono}\n
<b>Productos:</b>"""

        for p in carrito:
            mensaje += f"\n- {p['nombre']} ({p['cantidad']} x ${p['precio']:.2f}) = ${p['cantidad'] * p['precio']:.2f}"

        mensaje += f"""\n\n<b>Método de pago:</b> {pago}
<b>Total:</b> ${total:.2f}"""

        if ahorro > 0:
            mensaje += f"\n<b>Ahorro:</b> ${ahorro:.2f}"

        mensaje += f"\n\n<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        send_telegram_message(mensaje)

    except Exception as e:
        print(f"❌ Error al enviar notificación a Telegram: {e}")

    return render_template("confirmacion.html",
                           base_template=plantilla_base,
                           nombre=nombre,
                           direccion=direccion,
                           telefono=telefono,
                           numero_cliente=numero_cliente,
                           pago=pago,
                           carrito=carrito,
                           total=total,
                           ahorro=ahorro)


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
    # Cargar datos actualizados
    df_actual = pd.read_excel("productos.xlsx")

    # Estadísticas para el dashboard
    total_productos = len(df_actual)

    # Leer clientes desde el archivo CSV
    total_clientes = 0
    if os.path.exists("clientes.csv"):
        with open("clientes.csv", 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Restar 1 si hay encabezado
            total_clientes = sum(1 for row in reader) - 1
            if total_clientes < 0:
                total_clientes = 0

    # Obtener pedidos pendientes y últimos pedidos
    pedidos_pendientes = 0
    ultimos_pedidos = []
    ventas_totales = 0

    if os.path.exists("pedidos.csv"):
        with open("pedidos.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            pedidos = list(reader)

            # Contar pedidos pendientes
            pedidos_pendientes = sum(1 for p in pedidos if p["estado"] == "Pendiente")

            # Obtener los últimos 5 pedidos
            ultimos_pedidos = sorted(pedidos, key=lambda x: x["fecha"], reverse=True)[:5]
            ultimos_pedidos = [{
                "cliente": p["nombre"],
                "fecha": p["fecha"],
                "total": p["total"],
                "estado": p["estado"]
            } for p in ultimos_pedidos]

            # Calcular ventas totales (solo pedidos entregados)
            for p in pedidos:
                if p["estado"] == "Entregado":
                    try:
                        ventas_totales += float(p["total"])
                    except (ValueError, TypeError):
                        pass

    # Formatear ventas del mes
    ventas_mes = f"{ventas_totales:.2f}"

    # Productos con bajo stock (menos de 5 unidades)
    productos_bajo_stock = df_actual[df_actual['existencia'] < 5].to_dict(orient='records')

    return render_template('admin.html', 
                           total_productos=total_productos,
                           total_clientes=total_clientes,
                           pedidos_pendientes=pedidos_pendientes,
                           ventas_mes=ventas_mes,
                           productos_bajo_stock=productos_bajo_stock,
                           ultimos_pedidos=ultimos_pedidos)

@app.route('/admin/productos')
@admin_required
def admin_productos():
    # Cargar datos actualizados
    df_actual = pd.read_excel("productos.xlsx")

    # Paginación
    pagina_actual = int(request.args.get('pagina', 1))
    productos_por_pagina = 50
    total_productos = len(df_actual)
    total_paginas = (total_productos + productos_por_pagina - 1) // productos_por_pagina

    # Obtener productos para la página actual
    inicio = (pagina_actual - 1) * productos_por_pagina
    fin = inicio + productos_por_pagina
    productos_pagina = df_actual.iloc[inicio:fin].to_dict(orient='records')

    # Obtener categorías y departamentos únicos para los filtros
    categorias = sorted(df_actual['nombre_categoria'].dropna().unique())
    departamentos = sorted(df_actual['nombre_dep'].dropna().unique())

    return render_template('admin_productos.html', 
                           productos=productos_pagina,
                           categorias=categorias,
                           departamentos=departamentos,
                           pagina_actual=pagina_actual,
                           total_paginas=total_paginas)

@app.route('/admin/productos/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_producto_nuevo():
    global df
    df_actual = pd.read_excel("productos.xlsx")

    # Obtener categorías y departamentos únicos
    categorias = sorted(df_actual['nombre_categoria'].dropna().unique())
    departamentos = sorted(df_actual['nombre_dep'].dropna().unique())

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cbarras = request.form.get('cbarras')
            nombre_producto = request.form.get('nombre_producto')

            # Manejo de categoría
            if request.form.get('nombre_categoria') == 'nueva':
                nombre_categoria = request.form.get('nueva_categoria')
                if nombre_categoria not in categorias:
                    categorias.append(nombre_categoria)
            else:
                nombre_categoria = request.form.get('nombre_categoria')

            # Manejo de departamento
            if request.form.get('nombre_dep') == 'nuevo':
                nombre_dep = request.form.get('nuevo_departamento')
                if nombre_dep not in departamentos:
                    departamentos.append(nombre_dep)
            else:
                nombre_dep = request.form.get('nombre_dep')

            precio_venta = float(request.form.get('precio_venta'))
            precio_venta2 = request.form.get('precio_venta2')
            precio_venta2 = float(precio_venta2) if precio_venta2 else 0.0
            # Convertir primero a float y luego a int para manejar valores como '1.0'
            existencia = int(float(request.form.get('existencia')))

            # Manejar imagen si se proporciona
            imagen_filename = None
            if 'imagen' in request.files and request.files['imagen'].filename:
                imagen = request.files['imagen']
                if allowed_file(imagen.filename):
                    # Usar el código de barras como nombre de archivo
                    extension = os.path.splitext(imagen.filename)[1]
                    imagen_filename = f"{cbarras}{extension}"
                    imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)

                    # Si existe una imagen previa con el mismo nombre, eliminarla
                    if os.path.exists(imagen_path):
                        try:
                            os.remove(imagen_path)
                        except Exception as e:
                            print(f"Error al eliminar imagen previa: {e}")

                    imagen.save(imagen_path)

            # Verificar si el código de barras ya existe
            if cbarras in df_actual['cbarras'].values:
                return render_template('admin_producto_form.html', 
                                       error=True,
                                       mensaje=f"El código de barras {cbarras} ya existe",
                                       producto=None,
                                       categorias=categorias,
                                       departamentos=departamentos)

            # Crear nuevo producto como diccionario
            nuevo_producto = {
                'cbarras': cbarras,
                'nombre_producto': nombre_producto,
                'nombre_categoria': nombre_categoria,
                'nombre_dep': nombre_dep,
                'precio_venta': precio_venta,
                'precio_venta2': precio_venta2,
                'existencia': existencia,
                'imagen': imagen_filename
            }

            # Agregar el nuevo producto al DataFrame
            df_actual = pd.concat([df_actual, pd.DataFrame([nuevo_producto])], ignore_index=True)

            # Guardar cambios
            df_actual.to_excel("productos.xlsx", index=False)

            # Actualizar el DataFrame global
            df = df_actual

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
    global df
    df_actual = pd.read_excel("productos.xlsx")

    # Buscar el producto por código de barras
    producto = None
    for _, row in df_actual.iterrows():
        if str(row['cbarras']) == str(cbarras):
            producto = row.to_dict()
            break

    if not producto:
        return redirect(url_for('admin_productos'))

    # Obtener categorías y departamentos únicos
    categorias = sorted(df_actual['nombre_categoria'].dropna().unique())
    departamentos = sorted(df_actual['nombre_dep'].dropna().unique())

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre_producto = request.form.get('nombre_producto')

            # Manejo de categoría
            if request.form.get('nombre_categoria') == 'nueva':
                nombre_categoria = request.form.get('nueva_categoria')
                if nombre_categoria not in categorias:
                    categorias.append(nombre_categoria)
            else:
                nombre_categoria = request.form.get('nombre_categoria')

            # Manejo de departamento
            if request.form.get('nombre_dep') == 'nuevo':
                nombre_dep = request.form.get('nuevo_departamento')
                if nombre_dep not in departamentos:
                    departamentos.append(nombre_dep)
            else:
                nombre_dep = request.form.get('nombre_dep')

            precio_venta = float(request.form.get('precio_venta'))
            precio_venta2 = request.form.get('precio_venta2')
            precio_venta2 = float(precio_venta2) if precio_venta2 and precio_venta2.strip() else 0.0
            # Convertir primero a float y luego a int para manejar valores como '1.0'
            existencia = int(float(request.form.get('existencia')))

            # Manejar imagen si se proporciona
            imagen_filename = producto.get('imagen')
            if 'imagen' in request.files and request.files['imagen'].filename:
                imagen = request.files['imagen']
                if allowed_file(imagen.filename):
                    # Usar el código de barras como nombre de archivo
                    extension = os.path.splitext(imagen.filename)[1]
                    imagen_filename = f"{cbarras}{extension}"
                    imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)

                    # Si existe una imagen previa con el mismo nombre, eliminarla
                    if os.path.exists(imagen_path):
                        try:
                            os.remove(imagen_path)
                        except Exception as e:
                            print(f"Error al eliminar imagen previa: {e}")

                    imagen.save(imagen_path)

            # Actualizar el DataFrame
            for i, row in df_actual.iterrows():
                if str(row['cbarras']) == str(cbarras):
                    df_actual.at[i, 'nombre_producto'] = nombre_producto
                    df_actual.at[i, 'nombre_categoria'] = nombre_categoria
                    df_actual.at[i, 'nombre_dep'] = nombre_dep
                    df_actual.at[i, 'precio_venta'] = precio_venta
                    df_actual.at[i, 'precio_venta2'] = precio_venta2
                    df_actual.at[i, 'existencia'] = existencia
                    if imagen_filename:
                        df_actual.at[i, 'imagen'] = imagen_filename
                    break

            # Guardar cambios
            df_actual.to_excel("productos.xlsx", index=False)

            # Actualizar el DataFrame global
            df = df_actual

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
    global df
    df_actual = pd.read_excel("productos.xlsx")

    # Filtrar el DataFrame para eliminar el producto
    df_nuevo = df_actual[df_actual['cbarras'].astype(str) != str(cbarras)]

    # Si el tamaño cambió, significa que se eliminó un producto
    if len(df_nuevo) < len(df_actual):
        # Guardar cambios
        df_nuevo.to_excel("productos.xlsx", index=False)

        # Actualizar el DataFrame global
        df = df_nuevo

    return redirect(url_for('admin_productos'))

@app.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    # Verificar si existe el archivo de pedidos
    if not os.path.exists("pedidos.csv"):
        # Crear archivo con encabezados si no existe
        with open("pedidos.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "fecha", "nombre", "direccion", "colonia", "telefono", "metodo_pago", "total", "estado"])
        pedidos = []
    else:
        # Leer pedidos del archivo CSV
        pedidos = []
        with open("pedidos.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pedidos.append(row)

        # Ordenar por fecha descendente (más recientes primero)
        pedidos.reverse()

    return render_template('admin_pedidos.html', pedidos=pedidos)

@app.route('/admin/pedidos/detalle/<pedido_id>')
@admin_required
def admin_pedido_detalle(pedido_id):
    # Buscar el archivo de detalles del pedido
    detalle_filename = f"pedido_{pedido_id}_detalle.json"

    if not os.path.exists(detalle_filename):
        flash("No se encontró el detalle del pedido")
        return redirect(url_for('admin_pedidos'))

    # Cargar detalles del pedido
    with open(detalle_filename, "r", encoding="utf-8") as f:
        pedido = json.load(f)

    return render_template('admin_pedido_detalle.html', pedido=pedido)

@app.route('/admin/pedidos/estado/<pedido_id>/<nuevo_estado>')
@admin_required
def admin_pedido_estado(pedido_id, nuevo_estado):
    # Verificar que el estado sea válido
    estados_validos = ["Pendiente", "En proceso", "Enviado", "Entregado", "Cancelado"]
    if nuevo_estado not in estados_validos:
        flash("Estado no válido")
        return redirect(url_for('admin_pedidos'))

    # Actualizar el estado en el archivo CSV
    pedidos = []
    with open("pedidos.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] == pedido_id:
                row["estado"] = nuevo_estado
            pedidos.append(row)

    # Escribir de nuevo el archivo CSV
    with open("pedidos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "fecha", "nombre", "direccion", "colonia", "telefono", "metodo_pago", "total", "estado"])
        writer.writeheader()
        writer.writerows(pedidos)

    # Notificar por Telegram si se marca como enviado o entregado
    if nuevo_estado in ["Enviado", "Entregado"]:
        try:
            # Cargar datos del pedido
            detalle_filename = f"pedido_{pedido_id}_detalle.json"
            if os.path.exists(detalle_filename):
                with open(detalle_filename, "r", encoding="utf-8") as f:
                    pedido = json.load(f)

                from telegram_notifier import send_telegram_message
                cliente = pedido.get("cliente", {})
                mensaje = f"""<b>🔄 PEDIDO {nuevo_estado.upper()}</b>\n\n
<b>Cliente:</b> {cliente.get('nombre', 'N/A')}
<b>Dirección:</b> {cliente.get('direccion', 'N/A')}
<b>Teléfono:</b> {cliente.get('telefono', 'N/A')}\n
<b>Total:</b> ${pedido.get('total', 0):.2f}\n
<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"""

                send_telegram_message(mensaje)
        except Exception as e:
            print(f"❌ Error al enviar notificación de actualización: {e}")

    flash(f"Estado del pedido actualizado a {nuevo_estado}")
    return redirect(url_for('admin_pedidos'))

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
