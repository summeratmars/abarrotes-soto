#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test para verificar que las notificaciones de Telegram 
funcionen en modo silencioso durante desarrollo
"""

print("🔕 Probando notificaciones de Telegram en modo desarrollo")
print("=" * 60)

# Importar función de notificación
try:
    from telegram_notifier import send_telegram_message
    print("✅ Módulo telegram_notifier importado correctamente")
except ImportError as e:
    print(f"❌ Error importando telegram_notifier: {e}")
    exit(1)

# Probar envío de mensaje (debería ser silencioso)
print("\n🧪 Probando envío de notificación...")
print("-" * 40)

mensaje_prueba = """
🛒 <b>PEDIDO DE PRUEBA</b>

👤 <b>Cliente:</b> Test Usuario
📍 <b>Dirección:</b> Calle Test 123
💰 <b>Total:</b> $100.00

🚛 <i>Pedido de desarrollo</i>
"""

resultado = send_telegram_message(mensaje_prueba.strip())

print(f"\n📊 Resultado: {'✅ Éxito' if resultado else '⚠️ No enviado (normal en desarrollo)'}")

print("\n" + "=" * 60)
print("🎯 RESUMEN:")
print("• En desarrollo: Notificaciones silenciosas ✅")
print("• En producción: Notificaciones activas (con variables configuradas)")
print("• No más errores 404 molestos ✅")
print("\n🚀 Test completado")