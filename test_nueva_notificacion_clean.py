#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Archivo de prueba para la nueva notificación de Telegram mejorada
"""

from telegram_notifier import send_enhanced_telegram_notification
from datetime import datetime

def preview_telegram_message(nombre, direccion, colonia, telefono, numero_cliente, 
                           horario_entrega, info_pago, carrito, total, ahorro, folio):
    """Genera y muestra el mensaje sin enviarlo"""
    mensaje = f"""🛒 <b>NUEVO PEDIDO RECIBIDO</b>

👤 <b>DATOS DEL CLIENTE</b>
<b>Nombre:</b> {nombre}
<b>Dirección:</b> {direccion}
<b>Colonia:</b> {colonia}
<b>Teléfono:</b> {telefono}"""
    
    if numero_cliente:
        mensaje += f"\n<b>N° Cliente:</b> {numero_cliente}"
    
    mensaje += f"""

⏰ <b>HORARIO DE ENTREGA</b>
<b>{horario_entrega}</b>

💳 <b>MÉTODO DE PAGO</b>
{info_pago}"""

    # Agregar datos bancarios si es transferencia
    if 'transferencia' in info_pago.lower() or 'spei' in info_pago.lower():
        mensaje += f"""

🏦 <b>DATOS PARA TRANSFERENCIA</b>
<b>Banco:</b> BANAMEX
<b>Titular:</b> EFREN UZIEL SOTO JAIMES
<b>Tarjeta:</b> <code>5204 1662 0566 9791</code>

⚠️ <i>El cliente debe enviar comprobante de pago</i>"""

    mensaje += "\n\n📦 <b>PRODUCTOS PEDIDOS</b>"
    
    for producto in carrito:
        precio_unitario = producto['precio']
        cantidad = producto['cantidad']
        subtotal = precio_unitario * cantidad
        
        mensaje += f"\n• {producto['nombre']}"
        mensaje += f"\n  📊 {cantidad} x ${precio_unitario:.2f} = <b>${subtotal:.2f}</b>"
        
        # Mostrar descuento si existe
        if 'precio_original' in producto and producto['precio_original'] > precio_unitario:
            descuento_unitario = producto['precio_original'] - precio_unitario
            mensaje += f"\n  💸 Descuento: ${descuento_unitario:.2f} c/u"

    mensaje += f"""

💰 <b>RESUMEN FINANCIERO</b>
<b>Subtotal:</b> ${(total + ahorro):.2f}
<b>Descuentos:</b> -${ahorro:.2f}
<b>TOTAL A PAGAR:</b> ${total:.2f} ✅

📅 <b>INFORMACIÓN ADICIONAL</b>
<b>Fecha/Hora:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
<b>Folio:</b> #{folio}

📱 <b>CONTACTO DIRECTO</b>
<a href="https://wa.me/{telefono}">💬 Abrir chat de WhatsApp</a>

🚛 <i>Procesando pedido para entrega...</i>"""
    
    return mensaje

def test_notificacion_efectivo():
    """Prueba con método de pago en efectivo"""
    print("📱 Vista previa de notificación con EFECTIVO:")
    print("=" * 50)
    
    # Datos de prueba
    nombre = "Juan Pérez"
    direccion = "Calle Reforma 123"
    colonia = "VOLCANES 2"
    telefono = "5512345678"
    numero_cliente = "CLI00001"
    horario_entrega = "3:00 PM - 4:00 PM"
    info_pago = "Efectivo\nPaga con $500 (necesita cambio de $186.50)"
    folio = "12345"
    
    carrito = [
        {
            'nombre': 'Coca Cola 600ml',
            'precio': 18.50,
            'precio_original': 20.00,
            'cantidad': 2
        },
        {
            'nombre': 'Pan Bimbo Grande',
            'precio': 35.00,
            'cantidad': 1
        },
        {
            'nombre': 'Leche Lala 1L',
            'precio': 22.50,
            'precio_original': 25.00,
            'cantidad': 3
        }
    ]
    
    total = 313.50
    ahorro = 25.00
    
    # Mostrar vista previa del mensaje
    mensaje_preview = preview_telegram_message(
        nombre, direccion, colonia, telefono, numero_cliente,
        horario_entrega, info_pago, carrito, total, ahorro, folio
    )
    print(mensaje_preview)
    print("=" * 50)
    
    # Enviar usando la función mejorada (solo si hay configuración de Telegram)
    result = send_enhanced_telegram_notification(
        nombre, direccion, colonia, telefono, numero_cliente,
        horario_entrega, info_pago, carrito, total, ahorro, folio
    )
    
    if result:
        print("✅ Notificación de prueba enviada exitosamente")
    else:
        print("❌ Error al enviar notificación de prueba")

def test_notificacion_transferencia():
    """Prueba con método de pago por transferencia"""
    print("\n\n🏦 Probando notificación con TRANSFERENCIA:")
    print("=" * 60)
    
    # Datos de prueba para transferencia
    nombre = "María González"
    direccion = "Av. Insurgentes 456"
    colonia = "CENTRO"
    telefono = "5598765432"
    numero_cliente = "CLI00002"
    horario_entrega = "5:00 PM - 6:00 PM"
    info_pago = "Transferencia/SPEI\nTotal a transferir: $245.75"
    folio = "12346"
    
    carrito = [
        {
            'nombre': 'Arroz San Miguel 1kg',
            'precio': 28.00,
            'cantidad': 2
        },
        {
            'nombre': 'Aceite Capullo 1L',
            'precio': 45.75,
            'precio_original': 50.00,
            'cantidad': 1
        },
        {
            'nombre': 'Frijoles La Costeña 580g',
            'precio': 32.00,
            'cantidad': 3
        },
        {
            'nombre': 'Huevos San Juan 18 pzs',
            'precio': 55.00,
            'precio_original': 60.00,
            'cantidad': 1
        }
    ]
    
    total = 245.75
    ahorro = 9.25
    
    # Mostrar vista previa del mensaje
    mensaje_preview = preview_telegram_message(
        nombre, direccion, colonia, telefono, numero_cliente,
        horario_entrega, info_pago, carrito, total, ahorro, folio
    )
    print(mensaje_preview)
    print("=" * 60)
    
    # Enviar usando la función mejorada
    result = send_enhanced_telegram_notification(
        nombre, direccion, colonia, telefono, numero_cliente,
        horario_entrega, info_pago, carrito, total, ahorro, folio
    )
    
    if result:
        print("✅ Notificación de transferencia enviada exitosamente")
    else:
        print("❌ Error al enviar notificación de transferencia")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DE NOTIFICACIONES TELEGRAM")
    print("=" * 60)
    
    # Probar ambos métodos de pago
    test_notificacion_efectivo()
    test_notificacion_transferencia()
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")