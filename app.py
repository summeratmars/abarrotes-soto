from flask import Flask, render_template, request, jsonify, redirect
from email.mime.text import MIMEText
from flask import session  # ✅ necesario para usar sesiones
import smtplib
import pandas as pd
import json
import os
import csv



app = Flask(__name__)
app.secret_key = 'mexico'  # puede ser cualquier texto, pero debe estar

df = pd.read_excel("productos.xlsx")


@app.route("/")
def index():
    query = request.args.get("q", "")
    departamento = request.args.get("departamento", "")
    categoria = request.args.get("categoria", "")
    orden = request.args.get("orden", "")


    # Filtrar solo productos con existencia >= 1
    productos = df[df["existencia"] >= 1].copy()

    if departamento:
        productos = productos[productos["nombre_dep"] == departamento]
    if categoria:
        productos = productos[productos["nombre_categoria"] == categoria]
    if query:
        productos = productos[productos["nombre_producto"].str.contains(query, case=False, na=False)]
        # Ordenamiento
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
                           productos=productos.to_dict(orient="records"),
                           query=query,
                           departamento=departamento,
                           categoria=categoria,
                           departamentos=departamentos,
                           categorias=categorias)


@app.route('/cart')
def ver_carrito():
    return render_template('cart.html')

# En tu archivo app.py o main.py

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "GET":
        return render_template("checkout.html")
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
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()

        numero_cliente = generar_numero_cliente()

        # Guardar en CSV
        with open("clientes.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["cliente_id", "nombre", "telefono"])
            writer.writerow([numero_cliente, nombre, telefono])

        # Enviar por correo
        enviar_correo(nombre, telefono, numero_cliente)

        print(f"Registrado: {numero_cliente} - {nombre} - {telefono}")
        return render_template("monedero.html", mensaje=f"✅ Cliente registrado correctamente. Tu número de cliente es: {numero_cliente}")
    
    return render_template("monedero.html")




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
    return render_template("confirmacion.html",
                           nombre=session.get("nombre", "Cliente"),
                           direccion=session.get("direccion", ""),
                           telefono=session.get("telefono", ""),
                           numero_cliente=session.get("numero_cliente", ""),  # nuevo
                           pago=session.get("pago", ""),
                           carrito=session.get("carrito", []),
                           total=session.get("total", 0),
                           ahorro=session.get("ahorro", 0))

if __name__ == "__main__":
    app.run(debug=True)
