from flask import Flask, render_template, request, jsonify, redirect
from email.mime.text import MIMEText
from flask import session  # ✅ necesario para usar sesiones
from flask import Flask, request, render_template   
from datetime import datetime
from unidecode import unidecode
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import smtplib
import pandas as pd
import json
import os
import csv


app = Flask(__name__)
app.secret_key = 'mexico'  # puede ser cualquier texto, pero debe estar

df = pd.read_excel("productos.xlsx")

def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    return unidecode(texto.strip().lower())


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

    return render_template("index.html",
                       base_template=plantilla,
                       productos=productos.to_dict(orient="records"),
                       query=query,
                       departamento=departamento,
                       categoria=categoria,
                       departamentos=departamentos,
                       categorias=categorias)



@app.route('/cart')
def ver_carrito():
    plantilla_base = 'base_movil.html' if es_movil() else 'base_escritorio.html'
    return render_template('cart.html', base_template=plantilla_base)

# En tu archivo app.py o main.py

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


from datetime import datetime

@app.route("/confirmacion")
def confirmacion():
    nombre = session.get("nombre", "Cliente")
    direccion = session.get("direccion", "")
    telefono = session.get("telefono", "")
    numero_cliente = session.get("numero_cliente", "")
    pago = session.get("pago", "")
    carrito = session.get("carrito", [])
    total = session.get("total", 0)
    ahorro = session.get("ahorro", 0)

    plantilla_base = 'base_movil.html' if es_movil() else 'base_escritorio.html'

    # ✅ Crear ticket como archivo .txt
    try:
        now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        ruta_tickets = "/tmp/tickets"
        os.makedirs(ruta_tickets, exist_ok=True)
        nombre_archivo = f"pedido_{now}.txt"
        ruta_completa = os.path.join(ruta_tickets, nombre_archivo)

        # 1. Crear el archivo .txt
        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write("🛎️ NUEVO PEDIDO RECIBIDO — SURTIR URGENTE 🛒\n\n")
            f.write(f"👤 Cliente: {nombre}\n")
            f.write(f"📍 Dirección: {direccion}\n")
            f.write(f"📞 Teléfono: {telefono}\n\n")
            f.write("🧾 Productos:\n")
            for p in carrito:
                linea = f"- {p['nombre']} ({p['cantidad']} x ${p['precio']:.2f}) = ${p['cantidad'] * p['precio']:.2f}"
                f.write(linea + "\n")
            f.write(f"\n💳 Pago: {pago}\n")
            f.write(f"💰 Total: ${total:.2f}\n")
            if ahorro > 0:
                f.write(f"💸 Ahorro: ${ahorro:.2f}\n")
            f.write(f"\n📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

        # 2. Subirlo a Google Drive
        subir_a_drive(ruta_completa, nombre_archivo, "12jHX99skYS4usGGxn3IKJ642Ehe7dZYN")

    except Exception as e:
        print("❌ Error al generar archivo de ticket:", e)



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

def subir_a_drive(ruta_local, nombre_archivo, carpeta_drive_id):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(
        ''config_drive.txt'', scopes=SCOPES)

    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': nombre_archivo,
        'parents': [carpeta_drive_id]
    }
    media = MediaFileUpload(ruta_local, mimetype='text/plain')

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"📤 Archivo subido a Drive con ID: {file.get('id')}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
