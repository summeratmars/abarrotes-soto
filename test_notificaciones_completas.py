#!/usr/bin/env python3
"""
Script de prueba para la nueva notificación de Telegram mejorada
Simula un pedido completo con todos los nuevos campos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_notifier import send_enhanced_telegram_notification

def test_notificacion_completa():
    """Prueba la notificación completa con todos los campos nuevos"""
    
    # Datos del pedido simulado
    pedido_data = {
        'folio': '#12346',
        'nombre': 'María González',
        'direccion': 'Av. Constitución 456',
        'colonia': 'LA CONCHITA',
        'telefono': '5587654321',
        'numero_cliente': 'CLI00002',
        'horario_entrega': 'Lo antes posible',
        'pago': 'Transferencia',
        'info_pago': {
            'banco': 'BBVA Bancomer',
            'clabe': '012345678901234567',
            'nombre': 'Abarrotes Soto'
        },
        'carrito': [
            {
                'nombre': 'Coca Cola 2L',
                'cantidad': 2,
                'precio': 32.00,
                'precio_original': 35.00
            },
            {
                'nombre': 'Sabritas Clásicas',
                'cantidad': 3,
                'precio': 18.50,
                'precio_original': 18.50
            },
            {
                'nombre': 'Yogurt Danone 1L',
                'cantidad': 1,
                'precio': 28.00,
                'precio_original': 32.00
            }
        ],
        'total': 147.50,
        'ahorro': 13.00
    }
    
    print("🧪 Probando notificación completa de Telegram...")
    print("=" * 60)
    
    # Enviar notificación
    success = send_enhanced_telegram_notification(
        nombre=pedido_data['nombre'],
        direccion=pedido_data['direccion'],
        colonia=pedido_data['colonia'],
        telefono=pedido_data['telefono'],
        numero_cliente=pedido_data['numero_cliente'],
        horario_entrega=pedido_data['horario_entrega'],
        info_pago=pedido_data['info_pago'],
        carrito=pedido_data['carrito'],
        total=pedido_data['total'],
        ahorro=pedido_data['ahorro'],
        folio=pedido_data['folio']
    )
    
    if success:
        print("✅ Notificación enviada exitosamente")
    else:
        print("⚠️ Notificación generada pero no enviada (configuración de Telegram)")
    
    print("=" * 60)

def test_notificacion_tarjeta():
    """Prueba notificación con pago con tarjeta"""
    
    pedido_data = {
        'folio': '#12347',
        'nombre': 'Carlos Martínez',
        'direccion': 'Calle 5 de Mayo 789',
        'colonia': 'BARRIO SAN ANTONIO',
        'telefono': '5598765432',
        'numero_cliente': '',
        'horario_entrega': '6:00 PM - 7:00 PM',
        'pago': 'Tarjeta',
        'info_pago': {
            'mensaje': 'Nuestro repartidor llevará la terminal bancaria'
        },
        'carrito': [
            {
                'nombre': 'Arroz Blanco 1kg',
                'cantidad': 2,
                'precio': 22.50,
                'precio_original': 22.50
            },
            {
                'nombre': 'Aceite Capullo 1L',
                'cantidad': 1,
                'precio': 45.00,
                'precio_original': 48.00
            }
        ],
        'total': 90.00,
        'ahorro': 3.00
    }
    
    print("🧪 Probando notificación con pago por tarjeta...")
    print("=" * 60)
    
    success = send_enhanced_telegram_notification(
        nombre=pedido_data['nombre'],
        direccion=pedido_data['direccion'],
        colonia=pedido_data['colonia'],
        telefono=pedido_data['telefono'],
        numero_cliente=pedido_data['numero_cliente'],
        horario_entrega=pedido_data['horario_entrega'],
        info_pago=pedido_data['info_pago'],
        carrito=pedido_data['carrito'],
        total=pedido_data['total'],
        ahorro=pedido_data['ahorro'],
        folio=pedido_data['folio']
    )
    
    if success:
        print("✅ Notificación enviada exitosamente")
    else:
        print("⚠️ Notificación generada pero no enviada (configuración de Telegram)")
    
    print("=" * 60)

def test_notificacion_efectivo():
    """Prueba notificación con pago en efectivo"""
    
    pedido_data = {
        'folio': '#12348',
        'nombre': 'Ana Rodríguez',
        'direccion': 'Privada Los Pinos 321',
        'colonia': 'TERRA',
        'telefono': '5576543210',
        'numero_cliente': 'CLI00003',
        'horario_entrega': '9:00 AM - 10:00 AM',
        'pago': 'Efectivo',
        'info_pago': {
            'tipo': 'pago_justo'
        },
        'carrito': [
            {
                'nombre': 'Pan de Caja Bimbo',
                'cantidad': 1,
                'precio': 35.00,
                'precio_original': 35.00
            },
            {
                'nombre': 'Huevos San Juan 18pz',
                'cantidad': 1,
                'precio': 55.00,
                'precio_original': 60.00
            }
        ],
        'total': 90.00,
        'ahorro': 5.00
    }
    
    print("🧪 Probando notificación con pago justo en efectivo...")
    print("=" * 60)
    
    success = send_enhanced_telegram_notification(
        nombre=pedido_data['nombre'],
        direccion=pedido_data['direccion'],
        colonia=pedido_data['colonia'],
        telefono=pedido_data['telefono'],
        numero_cliente=pedido_data['numero_cliente'],
        horario_entrega=pedido_data['horario_entrega'],
        info_pago=pedido_data['info_pago'],
        carrito=pedido_data['carrito'],
        total=pedido_data['total'],
        ahorro=pedido_data['ahorro'],
        folio=pedido_data['folio']
    )
    
    if success:
        print("✅ Notificación enviada exitosamente")
    else:
        print("⚠️ Notificación generada pero no enviada (configuración de Telegram)")
    
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de notificaciones mejoradas de Telegram")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    test_notificacion_completa()
    test_notificacion_tarjeta()
    test_notificacion_efectivo()
    
    print("🎉 Todas las pruebas completadas")
    print("\n📝 NOTA: Para activar las notificaciones en producción:")
    print("   - Configura TELEGRAM_BOT_TOKEN en las variables de entorno")
    print("   - Configura TELEGRAM_CHAT_ID en las variables de entorno")
    print("   - Reinicia la aplicación en Render.com")