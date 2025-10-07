#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Archivo de prueba para la nueva notificación de Telegram mejorada
"""

from telegram_notifier import send_telegram_message
from datetime import datetime

def test_notificacion_mejorada():
    """Prueba la nueva notificación con formato mejorado"""
    
    # Datos de prueba
    nombre = "Juan Pérez"
    direccion = "Calle Reforma 123"
    colonia = "VOLCANES 2"
    telefono = "5512345678"
    numero_cliente = "CLI00001"
    horario_entrega = "3:00 PM - 4:00 PM"
    pago = "Efectivo"
    pago_efectivo_cambio = "si"
    pago_efectivo_monto = "500"
    total = 313.50
    ahorro = 25.00
    folio = "12345"
    fecha_hora_mx = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # Carrito de prueba
    carrito = [
        {
            "nombre": "Coca Cola 600ml",
            "cantidad": 2,
            "precio": 18.50,
            "precio_original": 20.00
        },
        {
            "nombre": "Pan Bimbo Grande",
            "cantidad": 1,
            "precio": 35.00,
            "precio_original": 35.00
        },
        {
            "nombre": "Leche Lala 1L",
            "cantidad": 3,
            "precio": 22.50,
            "precio_original": 25.00
        }
    ]
    
    # Crear enlace de WhatsApp
    telefono_limpio = telefono.replace(" ", "").replace("-", "")
    enlace_whatsapp = f"https://wa.me/{telefono_limpio}"

    # Determinar emoji para el horario
    horario_emoji = "🚀" if "antes posible" in horario_entrega.lower() else "⏰"
    
    # Determinar emoji y detalles para el método de pago
    if pago == "Efectivo":
        pago_emoji = "💵"
        if pago_efectivo_cambio == "si" and pago_efectivo_monto:
            pago_detalle = f"Paga con ${pago_efectivo_monto} (necesita cambio de ${float(pago_efectivo_monto) - total:.2f})"
        else:
            pago_detalle = "Pago justo (sin cambio)"
    elif pago == "Tarjeta":
        pago_emoji = "💳"
        pago_detalle = "Repartidor llevará terminal bancaria\n• Acepta débito y crédito\n• Visa, MasterCard, AmEx\n• Sin comisiones"
    elif pago == "Transferencia":
        pago_emoji = "🏦"
        pago_detalle = "SPEI/Transferencia bancaria\n• CLABE: 5204 1662 0566 9791\n• Banco: BANAMEX\n• A nombre de: EFREN UZIEL SOTO JAIMES"
    else:
        pago_emoji = "💰"
        pago_detalle = pago

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
<b>Folio:</b> #{folio}"""

    # Agregar enlace de WhatsApp con mejor formato
    mensaje += f"""\n\n📱 <b>CONTACTO DIRECTO</b>
<a href="{enlace_whatsapp}">💬 Abrir chat de WhatsApp</a>

🚛 <i>Procesando pedido para entrega...</i>"""

    print("📱 Vista previa del mensaje:")
    print("=" * 50)
    print(mensaje)
    print("=" * 50)
    
    # Enviar mensaje (descomenta la siguiente línea para enviar realmente)
    result = send_telegram_message(mensaje)
    
    if result:
        print("✅ Notificación de prueba enviada exitosamente")
    else:
        print("❌ Error al enviar notificación de prueba")

if __name__ == "__main__":
    test_notificacion_mejorada()