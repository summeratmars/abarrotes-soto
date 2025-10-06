# 📱 Configuración de Telegram para Notificaciones

## Variables de Entorno Requeridas

Para que las notificaciones de Telegram funcionen en producción, asegúrate de configurar estas variables de entorno:

### En Render.com (Producción):
```bash
TELEGRAM_BOT_TOKEN=tu_token_del_bot
TELEGRAM_CHAT_ID=tu_chat_id
```

### En Local (.env):
```bash
TELEGRAM_BOT_TOKEN=tu_token_del_bot
TELEGRAM_CHAT_ID=tu_chat_id
```

## Cómo Obtener el Token y Chat ID

### 1. Crear Bot de Telegram:
1. Habla con @BotFather en Telegram
2. Envía `/newbot`
3. Sigue las instrucciones
4. Guarda el token que te proporciona

### 2. Obtener Chat ID:
1. Envía un mensaje a tu bot
2. Visita: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
3. Busca el `chat.id` en la respuesta

## Características de las Nuevas Notificaciones

✅ **Información completa del cliente**
✅ **Horario de entrega específico** 
✅ **Detalles de pago (efectivo, tarjeta, transferencia)**
✅ **Productos con descuentos individuales**
✅ **Resumen financiero detallado**
✅ **Enlace directo a WhatsApp**
✅ **Formato profesional con HTML y emojis**
✅ **Mensaje de seguimiento para cambios de estado**

## Ejemplo de Notificación:

```
🛒 NUEVO PEDIDO RECIBIDO

👤 DATOS DEL CLIENTE
Nombre: Juan Pérez
Dirección: Calle Reforma 123
Colonia: VOLCANES 2
Teléfono: 5512345678

⏰ HORARIO DE ENTREGA
3:00 PM - 4:00 PM

💵 MÉTODO DE PAGO
Efectivo - Paga con $500 (necesita cambio de $186.50)

📦 PRODUCTOS PEDIDOS
• Coca Cola 600ml
  2 x $18.50 = $37.00
  💸 Descuento: $1.50 c/u

💰 TOTAL A PAGAR: $313.50

📱 CONTACTO DIRECTO
💬 Abrir chat de WhatsApp
```

## Notificaciones de Estado

El sistema también puede enviar notificaciones cuando cambie el estado del pedido:

```python
# Ejemplo de uso:
send_status_update_telegram(
    folio="12345",
    nuevo_estado="En preparación",
    tiempo_estimado="15-20 minutos"
)
```