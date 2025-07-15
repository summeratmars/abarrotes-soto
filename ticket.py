import win32print
import win32ui
from datetime import datetime

def imprimir_ticket(nombre, direccion, telefono, numero_cliente, pago, carrito, total, ahorro):
    nombre_impresora = "ZKP8008"
    hPrinter = win32print.OpenPrinter(nombre_impresora)
    hDC = win32print.GetPrinter(hPrinter, 2)
    pdc = win32ui.CreateDC()
    pdc.CreatePrinterDC(nombre_impresora)
    pdc.StartDoc("Pedido Abarrotes Soto")
    pdc.StartPage()

    y = 100
    salto = 20

    def escribir(texto, negrita=True):  # puedes dejarlo con ese nombre aunque ya siempre es negrita
        nonlocal y
        font = win32ui.CreateFont({
            "name": "Courier New",
            "height": 36,
            "weight": 700  # negrita forzada
        })
        pdc.SelectObject(font)
        pdc.TextOut(100, y, texto)
        y += 40



    
    escribir("Nuevo Pedido Recibido")
    escribir("----------------------------")
    escribir(f"Nombre: {nombre}")
    escribir(f"Dirección: {direccion}")
    escribir(f"Teléfono: {telefono}")
    escribir(f"Cliente: {numero_cliente}")
    ...
    escribir(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    escribir(f"Pago: {pago}")
    escribir("----------------------------")

    for p in carrito:
        nombre = p['nombre'][:22].ljust(22)
        cantidad = str(p['cantidad']).rjust(2)
        precio_unitario = f"${p['precio']:.2f}".rjust(8)
        subtotal = f"${p['precio'] * p['cantidad']:.2f}".rjust(8)
        escribir(f"{cantidad} x {nombre} {precio_unitario} {subtotal}")
       


    escribir("----------------------------")
    escribir(f"Total: ${total:.2f}")
    if ahorro > 0:
        escribir(f"Ahorro: ${ahorro:.2f}")
    escribir("")
    
        

    pdc.EndPage()
    pdc.EndDoc()
    pdc.DeleteDC()
