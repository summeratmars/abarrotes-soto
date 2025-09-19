#!/usr/bin/env python3
"""
Script de prueba para el sistema de notificaciones de imágenes faltantes
"""

import os
from notificador_imagenes import (
    verificar_imagen_producto,
    obtener_estadisticas_imagenes,
    cargar_productos_notificados
)

def test_productos_ejemplo():
    """Prueba el sistema con productos de ejemplo"""
    print("🧪 PRUEBA DEL SISTEMA DE NOTIFICACIONES DE IMÁGENES")
    print("=" * 60)
    
    # Productos de prueba - algunos pueden no tener imagen
    productos_prueba = [
        {"codigo": "75001186", "nombre": "LIMPIADOR FABULOSO MAR FRESCO 500ML"},
        {"codigo": "7500810000441", "nombre": "TAKIS ORIGINAL BARCEL 70G"},
        {"codigo": "7500478022373", "nombre": "GALLETAS EMPERADOR SENZO"},
        {"codigo": "090", "nombre": "AZUCAR"},
        {"codigo": "12345", "nombre": "PRODUCTO SIN IMAGEN EJEMPLO"},  # Este seguramente no tiene imagen
    ]
    
    print("📋 Verificando imágenes de productos...")
    print("-" * 40)
    
    for producto in productos_prueba:
        codigo = producto["codigo"]
        nombre = producto["nombre"]
        
        print(f"\n🔍 Verificando: {codigo} - {nombre}")
        
        # Verificar si existe imagen
        tiene_imagen = verificar_imagen_producto(codigo, nombre)
        
        if tiene_imagen:
            print(f"✅ Imagen encontrada para {codigo}")
        else:
            print(f"❌ Imagen NO encontrada para {codigo}")
            print(f"   📧 Se debería haber enviado notificación por Telegram")
    
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS DEL SISTEMA")
    print("-" * 40)
    
    # Obtener estadísticas
    stats = obtener_estadisticas_imagenes()
    print(f"📦 Total productos sin imagen notificados: {stats.get('productos_sin_imagen_total', 0)}")
    print(f"📅 Notificaciones enviadas hoy: {stats.get('notificados_hoy', 0)}")
    
    print("\n" + "=" * 60)
    print("📝 PRODUCTOS NOTIFICADOS")
    print("-" * 40)
    
    # Mostrar productos que han sido notificados
    notificados = cargar_productos_notificados()
    if notificados:
        for codigo, datos in notificados.items():
            print(f"📦 {codigo}: {datos.get('nombre', 'Sin nombre')}")
            print(f"   📅 Fecha: {datos.get('fecha', 'Sin fecha')}")
            print(f"   ✅ Notificado: {'Sí' if datos.get('notificado') else 'No'}")
            print()
    else:
        print("ℹ️ Ningún producto ha sido notificado aún.")
    
    print("=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("\n💡 NOTA: Las notificaciones por Telegram solo se envían una vez por día por producto.")
    print("   Si quieres probar el envío nuevamente, elimina el archivo:")
    print("   productos_sin_imagen_notificados.json")

if __name__ == "__main__":
    test_productos_ejemplo()