from dotenv import load_dotenv
load_dotenv()

from notificador_imagenes import verificar_imagen_producto
from telegram_notifier import send_telegram_message

print("=== PROBANDO ENVÍO DIRECTO DE TELEGRAM ===")
resultado = send_telegram_message("🧪 <b>PRUEBA DE NOTIFICACIÓN</b>\n\nEsta es una prueba para verificar que las notificaciones funcionan correctamente.\n\n✅ Si ves este mensaje, Telegram está funcionando!")
print(f"Mensaje enviado: {resultado}")

print("\n=== PROBANDO CON CÓDIGO DE BARRAS FICTICIO ===")
resultado2 = verificar_imagen_producto('0000000000000', 'Producto ficticio de prueba')
print(f"Imagen encontrada: {resultado2}")
