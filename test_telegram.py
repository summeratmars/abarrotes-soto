#!/usr/bin/env python
# Script para probar la integración con Telegram

import os
from telegram_notifier import send_telegram_message

# Este script verifica si las variables de entorno están configuradas
# y envía un mensaje de prueba al bot de Telegram

print("🔍 Comprobando configuración de Telegram...")

token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

if not token:
    print("❌ Error: La variable de entorno TELEGRAM_BOT_TOKEN no está configurada")
    print("   Para configurarla, ejecuta:")
    print("   export TELEGRAM_BOT_TOKEN=tu_token")
else:
    print("✅ Token de bot configurado")

if not chat_id:
    print("❌ Error: La variable de entorno TELEGRAM_CHAT_ID no está configurada")
    print("   Para configurarla, ejecuta:")
    print("   export TELEGRAM_CHAT_ID=tu_chat_id")
else:
    print("✅ Chat ID configurado")

if token and chat_id:
    print("\n📤 Enviando mensaje de prueba...")
    result = send_telegram_message("🧪 <b>Prueba de notificación</b>\n\nEste es un mensaje de prueba desde Abarrotes Soto.")

    if result:
        print("\n✅ Mensaje enviado correctamente. Por favor, verifica tu Telegram.")
    else:
        print("\n❌ Error al enviar el mensaje. Revisa los datos y tu conexión.")
else:
    print("\n⚠️ No se puede enviar el mensaje de prueba porque falta configuración.")
