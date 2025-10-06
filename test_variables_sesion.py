#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar que las variables de sesión se manejan correctamente
"""

def test_variables_pago():
    print("🧪 Probando manejo de variables de pago...")
    
    # Simular datos que vienen del formulario
    form_data = {
        'pago': 'Efectivo',
        'pago_efectivo_cambio': 'si',
        'pago_efectivo_monto': '500'
    }
    
    # Simular datos de sesión (como se guardarían)
    session = {
        'pago': form_data.get('pago'),
        'pago_efectivo_cambio': form_data.get('pago_efectivo_cambio', ''),
        'pago_efectivo_monto': form_data.get('pago_efectivo_monto', ''),
        'total': 313.50
    }
    
    # Simular recuperación de sesión (como en confirmacion())
    pago = session.get("pago", "")
    pago_efectivo_cambio = session.get("pago_efectivo_cambio", "")
    pago_efectivo_monto = session.get("pago_efectivo_monto", "")
    total = session.get("total", 0)
    
    print(f"✅ pago: '{pago}'")
    print(f"✅ pago_efectivo_cambio: '{pago_efectivo_cambio}'")
    print(f"✅ pago_efectivo_monto: '{pago_efectivo_monto}'")
    print(f"✅ total: {total}")
    
    # Probar lógica de notificación (como en el código real)
    if pago == "Efectivo":
        pago_emoji = "💵"
        if pago_efectivo_cambio == "si" and pago_efectivo_monto:
            try:
                monto = float(pago_efectivo_monto)
                cambio = monto - total
                pago_detalle = f"Paga con ${monto:.2f} (necesita cambio de ${cambio:.2f})"
                print(f"✅ Pago detalle calculado: '{pago_detalle}'")
            except (ValueError, TypeError) as e:
                pago_detalle = "Pago justo (sin cambio)"
                print(f"❌ Error en conversión: {e}")
                print(f"🔄 Fallback: '{pago_detalle}'")
        else:
            pago_detalle = "Pago justo (sin cambio)"
            print(f"✅ Pago detalle: '{pago_detalle}'")
    
    print("🎉 Prueba completada sin errores")

def test_variables_otros_pagos():
    print("\n🧪 Probando otros métodos de pago...")
    
    # Probar con tarjeta
    session_tarjeta = {'pago': 'Tarjeta', 'total': 313.50}
    pago = session_tarjeta.get("pago", "")
    
    if pago == "Tarjeta":
        pago_detalle = "Repartidor llevará terminal bancaria"
        print(f"✅ Tarjeta: '{pago_detalle}'")
    
    # Probar con transferencia
    session_transfer = {'pago': 'Transferencia', 'total': 313.50}
    pago = session_transfer.get("pago", "")
    
    if pago == "Transferencia":
        pago_detalle = "SPEI/Transferencia bancaria"
        print(f"✅ Transferencia: '{pago_detalle}'")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de variables de sesión")
    print("=" * 50)
    
    test_variables_pago()
    test_variables_otros_pagos()
    
    print("\n" + "=" * 50)
    print("✅ Todas las pruebas completadas exitosamente")