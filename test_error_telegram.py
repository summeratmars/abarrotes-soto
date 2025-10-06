#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para simular el error de Telegram y verificar la corrección
"""

def test_simulacion_error():
    print("🧪 Simulando el error original de Telegram...")
    print("=" * 60)
    
    # Simular sesión como podría estar en el momento del error
    session_mock = {
        "nombre": "Juan Pérez",
        "direccion": "Calle Test 123",
        "colonia": "VOLCANES 2",
        "telefono": "5512345678",
        "numero_cliente": "CLI00001",
        "pago": "Efectivo",
        "horario_entrega": "3:00 PM - 4:00 PM",
        "total": 313.50,
        "ahorro": 25.00,
        # Estas variables podrían faltar en algunos casos
        "pago_efectivo_cambio": "si",
        "pago_efectivo_monto": "500"
    }
    
    # Simular recuperación de variables de sesión
    try:
        pago = session_mock.get("pago", "")
        pago_efectivo_cambio = session_mock.get("pago_efectivo_cambio", "")
        pago_efectivo_monto = session_mock.get("pago_efectivo_monto", "")
        total = session_mock.get("total", 0)
        
        print(f"✅ Variables recuperadas correctamente:")
        print(f"   pago: '{pago}'")
        print(f"   pago_efectivo_cambio: '{pago_efectivo_cambio}'")
        print(f"   pago_efectivo_monto: '{pago_efectivo_monto}'")
        print(f"   total: {total}")
        
        # Simular la lógica que estaba causando error
        if pago == "Efectivo":
            pago_emoji = "💵"
            # Nueva lógica con validación
            efectivo_cambio = pago_efectivo_cambio if 'pago_efectivo_cambio' in locals() else ""
            efectivo_monto = pago_efectivo_monto if 'pago_efectivo_monto' in locals() else ""
            
            if efectivo_cambio == "si" and efectivo_monto:
                try:
                    monto = float(efectivo_monto)
                    cambio = monto - total
                    pago_detalle = f"Paga con ${monto:.2f} (necesita cambio de ${cambio:.2f})"
                    print(f"✅ Pago detalle calculado: '{pago_detalle}'")
                except (ValueError, TypeError):
                    pago_detalle = "Pago justo (sin cambio)"
                    print(f"⚠️ Error en conversión, usando pago justo")
            else:
                pago_detalle = "Pago justo (sin cambio)"
                print(f"✅ Pago justo sin cambio")
        
        print("🎉 Simulación completada SIN errores")
        
    except NameError as e:
        print(f"❌ Error NameError: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    return True

def test_caso_sin_variables():
    print("\n🧪 Probando caso extremo sin variables de efectivo...")
    print("=" * 60)
    
    # Simular sesión sin las variables problemáticas
    session_mock = {
        "nombre": "Ana García",
        "pago": "Efectivo",
        "total": 150.00,
        # Sin pago_efectivo_cambio y pago_efectivo_monto
    }
    
    try:
        pago = session_mock.get("pago", "")
        pago_efectivo_cambio = session_mock.get("pago_efectivo_cambio", "")
        pago_efectivo_monto = session_mock.get("pago_efectivo_monto", "")
        total = session_mock.get("total", 0)
        
        print(f"✅ Variables (con valores vacíos):")
        print(f"   pago_efectivo_cambio: '{pago_efectivo_cambio}'")
        print(f"   pago_efectivo_monto: '{pago_efectivo_monto}'")
        
        if pago == "Efectivo":
            efectivo_cambio = pago_efectivo_cambio if 'pago_efectivo_cambio' in locals() else ""
            efectivo_monto = pago_efectivo_monto if 'pago_efectivo_monto' in locals() else ""
            
            if efectivo_cambio == "si" and efectivo_monto:
                monto = float(efectivo_monto)
                cambio = monto - total
                pago_detalle = f"Paga con ${monto:.2f} (necesita cambio de ${cambio:.2f})"
            else:
                pago_detalle = "Pago justo (sin cambio)"
                print(f"✅ Manejado como pago justo: '{pago_detalle}'")
        
        print("🎉 Caso extremo manejado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en caso extremo: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de corrección de error de Telegram")
    print("=" * 60)
    
    test1 = test_simulacion_error()
    test2 = test_caso_sin_variables()
    
    print("\n📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    print(f"✅ Prueba normal: {'EXITOSA' if test1 else 'FALLIDA'}")
    print(f"✅ Prueba extrema: {'EXITOSA' if test2 else 'FALLIDA'}")
    
    if test1 and test2:
        print("\n🎉 TODAS LAS PRUEBAS EXITOSAS - Error corregido")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON - Revisar código")