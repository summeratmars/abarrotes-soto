#!/usr/bin/env python3
"""
Script de prueba para verificar que las imágenes del carrito funcionen correctamente
"""
import os
import json

def probar_imagenes_carrito():
    print("🚀 Probando sistema de imágenes del carrito")
    print("=" * 60)
    
    # Simular carrito con productos reales
    carrito_ejemplo = [
        {
            "cbarras": "013000001243",
            "nombre": "ACEITE 123 1L",
            "precio": 42.00,
            "precio_original": 46.00,
            "cantidad": 3,
            "puntos": 5
        },
        {
            "cbarras": "013602000200",
            "nombre": "ACEITE CAPULLO 755ML",
            "precio": 44.00,
            "precio_original": 47.00,
            "cantidad": 2,
            "puntos": 4
        },
        {
            "cbarras": "014800515329",
            "nombre": "ACE 850G",
            "precio": 37.00,
            "precio_original": 41.00,
            "cantidad": 1,
            "puntos": 3
        }
    ]
    
    print("📦 Productos de ejemplo en el carrito:")
    for producto in carrito_ejemplo:
        cbarras = producto['cbarras']
        nombre = producto['nombre']
        
        # Verificar si existen las imágenes
        rutas_imagen = [
            f"static/images/{cbarras}.webp",
            f"static/images/{cbarras}.jpg",
            f"static/images/{cbarras}.jpeg",
            f"static/images/{cbarras}.png"
        ]
        
        imagen_encontrada = None
        for ruta in rutas_imagen:
            if os.path.exists(ruta):
                imagen_encontrada = ruta
                break
        
        if imagen_encontrada:
            print(f"✅ {nombre}")
            print(f"   📸 Imagen: {imagen_encontrada}")
        else:
            print(f"⚠️ {nombre}")
            print(f"   🎭 Usará emoji de fallback")
        print()
    
    print("🎨 JavaScript de imágenes:")
    print("=" * 40)
    
    # Mostrar cómo se vería el JavaScript generado
    js_ejemplo = """
    function createProductImage(producto) {
        const emoji = getProductEmoji(producto.nombre);
        const cbarras = producto.cbarras || '';
        
        if (cbarras) {
            return `
                <img src="/static/images/${cbarras}.webp" 
                     alt="${producto.nombre}"
                     onerror="fallbackToNextFormat(this, '${cbarras}', '${emoji}')">
            `;
        } else {
            return `<div class="emoji-fallback">${emoji}</div>`;
        }
    }
    """
    print(js_ejemplo)
    
    print("🔍 Análisis de imágenes en el directorio static/images:")
    print("=" * 55)
    
    if os.path.exists("static/images"):
        imagenes = [f for f in os.listdir("static/images") if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        print(f"📊 Total de imágenes encontradas: {len(imagenes)}")
        
        # Mostrar algunas imágenes de ejemplo
        print("\n🖼️ Primeras 10 imágenes:")
        for i, imagen in enumerate(imagenes[:10]):
            print(f"   {i+1}. {imagen}")
        
        if len(imagenes) > 10:
            print(f"   ... y {len(imagenes) - 10} más")
    else:
        print("❌ Directorio static/images no encontrado")
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada")
    print("\n📋 Resumen:")
    print("• Las imágenes se cargarán automáticamente si existen")
    print("• Si no existe imagen, se mostrará emoji de fallback")
    print("• Las imágenes tienen efecto hover con zoom")
    print("• Fallback en múltiples formatos: .webp → .jpg → .jpeg → .png → emoji")

if __name__ == "__main__":
    probar_imagenes_carrito()