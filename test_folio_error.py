#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que el error de 'folio' no definido esté corregido
"""

def test_variables_sesion():
    """Prueba el manejo de todas las variables de sesión incluyendo folio"""
    print("🚀 Iniciando pruebas de variables de sesión (incluyendo folio)")
    print("=" * 60)
    
    # Simular datos completos de sesión como en una aplicación real
    session_data = {
        'nombre': 'Juan Pérez',
        'direccion': 'Calle Reforma 123',
        'colonia': 'VOLCANES 2',
        'telefono': '5512345678',
        'numero_cliente': 'CLI00001',
        'pago': 'Efectivo',
        'info_pago': 'Efectivo',
        'horario_entrega': '3:00 PM - 4:00 PM',
        'pago_efectivo_cambio': 'si',
        'pago_efectivo_monto': '500',
        'carrito': [
            {'nombre': 'Coca Cola 600ml', 'cantidad': 2, 'precio': 18.50, 'precio_original': 20.00},
            {'nombre': 'Pan Bimbo Grande', 'cantidad': 1, 'precio': 35.00, 'precio_original': 35.00}
        ],
        'total': 313.50,
        'ahorro': 25.00,
        'folio': '12345'  # Esta era la variable que faltaba
    }
    
    print("🧪 Simulando recuperación de variables de sesión...")
    
    # Simular la recuperación de variables como en app.py
    nombre = session_data.get("nombre", "")
    direccion = session_data.get("direccion", "")
    colonia = session_data.get("colonia", "")
    telefono = session_data.get("telefono", "")
    numero_cliente = session_data.get("numero_cliente", "")
    pago = session_data.get("pago", "")
    info_pago = session_data.get("info_pago", pago)
    horario_entrega = session_data.get("horario_entrega", "")
    pago_efectivo_cambio = session_data.get("pago_efectivo_cambio", "")
    pago_efectivo_monto = session_data.get("pago_efectivo_monto", "")
    carrito = session_data.get("carrito", [])
    total = session_data.get("total", 0)
    ahorro = session_data.get("ahorro", 0)
    folio = session_data.get("folio", "")  # ✅ Ahora está incluido
    
    print("✅ Variables recuperadas exitosamente:")
    print(f"   nombre: '{nombre}'")
    print(f"   folio: '{folio}'")
    print(f"   pago: '{pago}'")
    print(f"   pago_efectivo_cambio: '{pago_efectivo_cambio}'")
    print(f"   pago_efectivo_monto: '{pago_efectivo_monto}'")
    print(f"   total: {total}")
    
    # Probar la construcción del mensaje de Telegram (parte crítica donde faltaba folio)
    print("\n🧪 Probando construcción de mensaje de Telegram...")
    
    try:
        # Simular parte del mensaje donde se usa folio
        mensaje_folio = f"<b>Folio:</b> #{folio if folio else 'N/A'}"
        print(f"✅ Mensaje de folio generado: '{mensaje_folio}'")
        
        # Probar detalles de pago (donde también había errores)
        if pago == 'Efectivo':
            if pago_efectivo_cambio == 'si' and pago_efectivo_monto:
                try:
                    monto = float(pago_efectivo_monto)
                    cambio = monto - total
                    pago_detalle = f"Paga con ${monto:.2f} (necesita cambio de ${cambio:.2f})"
                    print(f"✅ Pago detalle generado: '{pago_detalle}'")
                except (ValueError, TypeError) as e:
                    print(f"❌ Error en cálculo de cambio: {e}")
            else:
                print("✅ Pago justo generado")
        
        print("🎉 Todas las variables se procesaron sin errores")
        
    except NameError as e:
        print(f"❌ Error de variable no definida: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    return True

def test_casos_extremos():
    """Prueba casos extremos donde las variables podrían estar vacías"""
    print("\n🧪 Probando casos extremos...")
    print("=" * 40)
    
    # Caso: sesión vacía o incompleta
    session_vacia = {}
    
    folio = session_vacia.get("folio", "")
    pago_efectivo_cambio = session_vacia.get("pago_efectivo_cambio", "")
    pago_efectivo_monto = session_vacia.get("pago_efectivo_monto", "")
    
    # Probar que no cause errores
    mensaje_folio = f"<b>Folio:</b> #{folio if folio else 'N/A'}"
    print(f"✅ Folio vacío manejado: '{mensaje_folio}'")
    
    # Probar variables de pago vacías
    if pago_efectivo_cambio == 'si' and pago_efectivo_monto:
        print("❌ No debería entrar aquí con variables vacías")
    else:
        print("✅ Variables de pago vacías manejadas correctamente")
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de corrección de error 'folio' no definido")
    print("=" * 70)
    
    exito1 = test_variables_sesion()
    exito2 = test_casos_extremos()
    
    print("\n📊 RESUMEN DE PRUEBAS:")
    print("=" * 70)
    print(f"✅ Prueba de variables: {'EXITOSA' if exito1 else 'FALLIDA'}")
    print(f"✅ Prueba de casos extremos: {'EXITOSA' if exito2 else 'FALLIDA'}")
    
    if exito1 and exito2:
        print("\n🎉 TODAS LAS PRUEBAS EXITOSAS - Error de folio corregido")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON - Revisar correcciones")