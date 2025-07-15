# Configuración del Bot de Telegram para Notificaciones de Pedidos

## Paso 1: Crear un Bot de Telegram

1. Abre Telegram y busca a `@BotFather`
2. Inicia una conversación y envía el comando `/newbot`
3. Sigue las instrucciones para crear el bot (nombre y username)
4. Al finalizar, recibirás un token de API como este: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`
5. **IMPORTANTE**: Guarda este token de forma segura y no lo compartas ni lo subas a GitHub

## Paso 2: Obtener el Chat ID

1. Inicia una conversación con tu nuevo bot
2. Envía cualquier mensaje a tu bot
3. Visita esta URL (reemplaza `<TU_TOKEN>` con el token que recibiste): 
   `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
4. Busca el valor `"id"` dentro de `"chat"` en la respuesta JSON
5. Este número es tu Chat ID (puede ser negativo para grupos)

## Paso 3: Configurar Variables de Entorno en Render

1. Ve al panel de control de tu aplicación en Render
2. Navega a la sección "Environment Variables"
3. Agrega estas dos variables:
   - `TELEGRAM_BOT_TOKEN`: El token que recibiste de BotFather
   - `TELEGRAM_CHAT_ID`: El chat ID que obtuviste en el paso anterior

## Funcionamiento

Cuando un cliente realiza un pedido, recibirás una notificación en Telegram con los detalles del pedido, incluyendo:

- Nombre del cliente
- Dirección de entrega
- Teléfono
- Lista de productos
- Total a pagar
- Método de pago

## Solución de problemas

Si no recibes notificaciones:

1. Verifica que las variables de entorno estén configuradas correctamente
2. Asegúrate de haber iniciado una conversación con tu bot
3. Revisa los logs de la aplicación para ver si hay errores en el envío
