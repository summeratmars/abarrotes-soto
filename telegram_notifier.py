import requests
import os
import json

# Obtener token y chat_id desde variables de entorno
def send_telegram_message(message):
    """Envía un mensaje al bot de Telegram con formato mejorado"""
    try:
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')

        # Si no hay token o chat_id configurados, modo silencioso (desarrollo)
        if not token or not chat_id:
            print("ℹ️ Notificaciones Telegram deshabilitadas (desarrollo)")
            return False

        # Validar formato básico del token
        if not token.startswith('bot') and ':' not in token:
            print("❌ Token de Telegram mal formado")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,  # Permitir preview de enlaces
            "disable_notification": False  # Permitir notificaciones
        }

        # Convertir a formato JSON para headers
        headers = {'Content-Type': 'application/json'}
        json_payload = json.dumps(payload, ensure_ascii=False)

        response = requests.post(url, data=json_payload.encode('utf-8'), headers=headers, timeout=10)

        if response.status_code == 200:
            print("✅ Notificación completa enviada a Telegram")
            return True
        else:
            error_data = response.text
            try:
                error_json = response.json()
                error_code = error_json.get('error_code', 'unknown')
                description = error_json.get('description', 'Unknown error')
                
                # Mensajes específicos según el error
                if error_code == 404:
                    print(f"❌ Error 404 Telegram: Bot no encontrado o token inválido")
                    print(f"   → Verifica TELEGRAM_BOT_TOKEN: {token[:10]}...")
                elif error_code == 400:
                    if 'chat not found' in description.lower():
                        print(f"❌ Error 400 Telegram: Chat no encontrado")
                        print(f"   → Verifica TELEGRAM_CHAT_ID: {chat_id}")
                        print(f"   → Asegúrate de haber iniciado una conversación con el bot")
                    else:
                        print(f"❌ Error 400 Telegram: {description}")
                elif error_code == 401:
                    print(f"❌ Error 401 Telegram: Token no autorizado")
                    print(f"   → Verifica que el token sea correcto")
                else:
                    print(f"❌ Error {error_code} Telegram: {description}")
                    
            except:
                print(f"❌ Error al enviar notificación a Telegram: {error_data}")
            
            return False

    except requests.exceptions.Timeout:
        print("❌ Timeout al conectar con Telegram")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión con Telegram")
        return False
    except Exception as e:
        print(f"❌ Error inesperado en Telegram: {e}")
        return False

def test_telegram_configuration():
    """Prueba la configuración de Telegram y da sugerencias"""
    print("🔍 Verificando configuración de Telegram...")
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN no está configurado")
        print("   → Configura la variable de entorno con tu token de bot")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID no está configurado") 
        print("   → Configura la variable de entorno con tu chat ID")
        return False
    
    print(f"✅ Token encontrado: {token[:10]}...")
    print(f"✅ Chat ID encontrado: {chat_id}")
    
    # Probar conexión con getMe
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_data = bot_info.get('result', {})
                print(f"✅ Bot conectado: @{bot_data.get('username', 'unknown')}")
                print(f"   → Nombre: {bot_data.get('first_name', 'N/A')}")
                return True
            else:
                print("❌ El bot no respondió correctamente")
                return False
        else:
            print(f"❌ Error al conectar con el bot: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar conexión: {e}")
        return False

def send_order_status_update(folio, estado, detalles=""):
    """Envía actualización de estado del pedido"""
    try:
        estado_emojis = {
            "Confirmado": "✅",
            "Preparando": "👨‍🍳",
            "En camino": "🚛",
            "Entregado": "📦✅",
            "Cancelado": "❌"
        }
        
        emoji = estado_emojis.get(estado, "📋")
        
        mensaje = f"""{emoji} <b>ACTUALIZACIÓN DE PEDIDO #{folio}</b>

<b>Estado:</b> {estado}"""
        
        if detalles:
            mensaje += f"\n<b>Detalles:</b> {detalles}"
            
        from datetime import datetime
        mensaje += f"\n\n<i>Actualización enviada: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>"
        
        return send_telegram_message(mensaje)
        
    except Exception as e:
        print(f"❌ Error al enviar actualización de estado: {e}")
        return False

def send_daily_summary():
    """Envía resumen diario de pedidos (función para uso futuro)"""
    try:
        from datetime import datetime
        fecha_hoy = datetime.now().strftime('%d/%m/%Y')
        
        mensaje = f"""📊 <b>RESUMEN DIARIO - {fecha_hoy}</b>

<b>Pedidos del día:</b> En desarrollo...
<b>Ventas totales:</b> En desarrollo...
<b>Productos más vendidos:</b> En desarrollo...

<i>Esta funcionalidad se activará próximamente</i>"""
        
        return send_telegram_message(mensaje)
        
    except Exception as e:
        print(f"❌ Error al enviar resumen diario: {e}")
        return False

def send_enhanced_telegram_notification(nombre, direccion, colonia, telefono, numero_cliente, 
                                      horario_entrega, info_pago, carrito, total, ahorro, folio):
    """Envía notificación completa y mejorada del pedido a Telegram"""
    try:
        from datetime import datetime
        
        # Construir mensaje completo
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
{info_pago}

📦 <b>PRODUCTOS PEDIDOS</b>"""
        
        # Agregar productos
        for producto in carrito:
            precio_unitario = producto.get('precio', 0)
            cantidad = producto.get('cantidad', 1)
            subtotal_producto = precio_unitario * cantidad
            precio_original = producto.get('precio_original', precio_unitario)
            
            mensaje += f"\n• {producto.get('nombre', 'Producto')}"
            mensaje += f"\n  📊 {cantidad} x ${precio_unitario:.2f} = <b>${subtotal_producto:.2f}</b>"
            
            # Mostrar descuento si existe
            if precio_original > precio_unitario:
                descuento_unitario = precio_original - precio_unitario
                mensaje += f"\n  💸 Descuento: ${descuento_unitario:.2f} c/u"
        
        # Resumen financiero
        mensaje += f"""

💰 <b>RESUMEN FINANCIERO</b>
<b>Subtotal:</b> ${total + ahorro:.2f}"""
        
        if ahorro > 0:
            mensaje += f"\n<b>Descuentos:</b> -${ahorro:.2f}"
        
        mensaje += f"\n<b>TOTAL A PAGAR:</b> ${total:.2f} ✅"
        
        # Información adicional
        fecha_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
        mensaje += f"""

📅 <b>INFORMACIÓN ADICIONAL</b>
<b>Fecha/Hora:</b> {fecha_hora}
<b>Folio:</b> #{folio}

📱 <b>CONTACTO DIRECTO</b>
<a href="https://wa.me/{telefono}">💬 Abrir chat de WhatsApp</a>

🚛 <i>Procesando pedido para entrega...</i>"""
        
        return send_telegram_message(mensaje)
        
    except Exception as e:
        print(f"❌ Error al enviar notificación mejorada: {e}")
        return False
