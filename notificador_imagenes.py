import os
import json
from datetime import datetime, timedelta
from telegram_notifier import send_telegram_message

# Archivo para rastrear productos ya notificados
ARCHIVO_NOTIFICADOS = 'productos_sin_imagen_notificados.json'

def cargar_productos_notificados():
    """Carga la lista de productos que ya fueron notificados"""
    try:
        if os.path.exists(ARCHIVO_NOTIFICADOS):
            with open(ARCHIVO_NOTIFICADOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error al cargar productos notificados: {e}")
        return {}

def guardar_productos_notificados(notificados):
    """Guarda la lista de productos notificados"""
    try:
        with open(ARCHIVO_NOTIFICADOS, 'w', encoding='utf-8') as f:
            json.dump(notificados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al guardar productos notificados: {e}")

def verificar_imagen_producto(codigo_barras, nombre_producto=""):
    """
    Verifica si un producto tiene imagen real o usa sinfoto.png
    Si no tiene imagen real, envía notificación por Telegram (solo una vez por día)
    """
    try:
        # Rutas de imágenes posibles
        extensiones = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
        imagen_encontrada = False
        
        for ext in extensiones:
            imagen_path = os.path.join('static', 'images', f"{codigo_barras}{ext}")
            if os.path.exists(imagen_path):
                imagen_encontrada = True
                break
        
        # Si no se encontró imagen real, procesar notificación
        if not imagen_encontrada:
            procesar_notificacion_sin_imagen(codigo_barras, nombre_producto)
            
        return imagen_encontrada
        
    except Exception as e:
        print(f"Error al verificar imagen del producto {codigo_barras}: {e}")
        return False

def procesar_notificacion_sin_imagen(codigo_barras, nombre_producto=""):
    """
    Procesa la notificación para un producto sin imagen
    Solo envía una notificación por día por producto
    """
    try:
        notificados = cargar_productos_notificados()
        hoy = datetime.now().strftime("%Y-%m-%d")
        
        # Verificar si ya fue notificado hoy
        if codigo_barras in notificados:
            ultima_notificacion = notificados[codigo_barras].get('fecha', '')
            if ultima_notificacion == hoy:
                return  # Ya fue notificado hoy
        
        # Enviar notificación por Telegram
        mensaje = f"""🖼️ <b>PRODUCTO SIN IMAGEN</b>
        
📊 <b>Código:</b> {codigo_barras}
📦 <b>Producto:</b> {nombre_producto or "Sin nombre"}
📅 <b>Fecha:</b> {datetime.now().strftime("%d/%m/%Y %H:%M")}

⚠️ Este producto está usando la imagen por defecto (sinfoto.png)
📸 Por favor agregar imagen real del producto"""

        if send_telegram_message(mensaje):
            # Registrar la notificación
            notificados[codigo_barras] = {
                'nombre': nombre_producto,
                'fecha': hoy,
                'notificado': True
            }
            guardar_productos_notificados(notificados)
            print(f"✅ Notificación enviada para producto sin imagen: {codigo_barras}")
        else:
            print(f"❌ Error al enviar notificación para producto: {codigo_barras}")
            
    except Exception as e:
        print(f"Error al procesar notificación para {codigo_barras}: {e}")

def limpiar_notificaciones_antiguas():
    """
    Limpia notificaciones de más de 7 días para permitir re-notificar
    """
    try:
        notificados = cargar_productos_notificados()
        fecha_limite = datetime.now() - timedelta(days=7)
        fecha_limite_str = fecha_limite.strftime("%Y-%m-%d")
        
        notificados_actualizados = {}
        for codigo, datos in notificados.items():
            if datos.get('fecha', '') >= fecha_limite_str:
                notificados_actualizados[codigo] = datos
        
        if len(notificados_actualizados) < len(notificados):
            guardar_productos_notificados(notificados_actualizados)
            print(f"🧹 Limpiadas {len(notificados) - len(notificados_actualizados)} notificaciones antiguas")
            
    except Exception as e:
        print(f"Error al limpiar notificaciones antiguas: {e}")

def obtener_estadisticas_imagenes():
    """
    Devuelve estadísticas de productos con y sin imagen
    """
    try:
        notificados = cargar_productos_notificados()
        hoy = datetime.now().strftime("%Y-%m-%d")
        
        # Contar productos notificados hoy
        notificados_hoy = sum(1 for datos in notificados.values() 
                             if datos.get('fecha') == hoy)
        
        return {
            'productos_sin_imagen_total': len(notificados),
            'notificados_hoy': notificados_hoy,
            'ultima_limpieza': hoy
        }
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return {}

# Ejecutar limpieza automática al importar el módulo
limpiar_notificaciones_antiguas()