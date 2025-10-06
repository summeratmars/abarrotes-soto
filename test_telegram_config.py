#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de diagnóstico para configuración de Telegram
Ayuda a identificar problemas con el bot de Telegram
"""

import os
import sys
from telegram_notifier import test_telegram_configuration, send_telegram_message

def main():
    print("🤖 Diagnóstico de Configuración de Telegram")
    print("=" * 60)
    
    # Verificar configuración
    config_ok = test_telegram_configuration()
    
    if not config_ok:
        print("\n❌ La configuración de Telegram tiene problemas")
        print("\n📋 PASOS PARA CONFIGURAR TELEGRAM:")
        print("1. Crear un bot en @BotFather")
        print("2. Obtener el token del bot")
        print("3. Iniciar conversación con el bot")
        print("4. Obtener tu chat ID enviando mensaje a @userinfobot")
        print("5. Configurar variables de entorno:")
        print("   TELEGRAM_BOT_TOKEN=tu_token_aqui")
        print("   TELEGRAM_CHAT_ID=tu_chat_id_aqui")
        return
    
    print("\n✅ Configuración básica correcta")
    
    # Probar envío de mensaje
    print("\n🧪 Probando envío de mensaje de prueba...")
    test_message = """🧪 <b>MENSAJE DE PRUEBA</b>

✅ La configuración de Telegram está funcionando correctamente.

📱 <b>Información del sistema:</b>
• Fecha: {fecha}
• Estado: Funcionando

🎉 ¡Tu bot está listo para recibir notificaciones de pedidos!"""
    
    from datetime import datetime
    test_message = test_message.format(fecha=datetime.now().strftime("%d/%m/%Y %H:%M"))
    
    success = send_telegram_message(test_message)
    
    if success:
        print("🎉 ¡Mensaje de prueba enviado exitosamente!")
        print("   → Revisa tu chat de Telegram")
    else:
        print("❌ Error al enviar mensaje de prueba")
        print("   → Revisa los logs arriba para más detalles")

if __name__ == "__main__":
    main()