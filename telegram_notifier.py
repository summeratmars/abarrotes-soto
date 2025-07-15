import requests
import os
import json

# Obtener token y chat_id desde variables de entorno
def send_telegram_message(message):
    """Envía un mensaje al bot de Telegram"""
    try:
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')

        # Si no hay token o chat_id configurados, no hacer nada
        if not token or not chat_id:
            print("⚠️ Notificación de Telegram desactivada: falta token o chat_id")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        # Convertir a formato JSON para headers
        headers = {'Content-Type': 'application/json'}
        json_payload = json.dumps(payload)

        response = requests.post(url, data=json_payload, headers=headers)

        if response.status_code == 200:
            print("✅ Notificación enviada a Telegram")
            return True
        else:
            print(f"❌ Error al enviar notificación a Telegram: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en Telegram: {e}")
        return False
