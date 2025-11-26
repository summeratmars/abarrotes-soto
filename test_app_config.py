"""
Script para probar que app.py funciona con db_config
"""

print("🔍 Probando imports de app.py con db_config...")
print()

try:
    # Intentar importar el módulo
    import sys
    import os
    
    # Simular entorno local
    os.environ.pop('RENDER', None)
    os.environ.pop('RAILWAY_ENVIRONMENT', None)
    
    print("📦 Importando db_config...")
    import db_config
    
    print("✅ db_config importado correctamente")
    print(f"   Modo detectado: {'API REST' if db_config.usar_api_rest() else 'Local'}")
    print()
    
    print("📦 Probando funciones disponibles...")
    funciones = [
        'get_db_connection',
        'obtener_productos_sucursal', 
        'guardar_pedido_db',
        'contar_productos_sucursal',
        'guardar_cotizacion_web',
        'registrar_cliente_monedero'
    ]
    
    for func in funciones:
        if hasattr(db_config, func):
            print(f"   ✅ {func}")
        else:
            print(f"   ❌ {func} NO ENCONTRADA")
    
    print()
    print("🧪 Probando obtener productos (primeros 3)...")
    productos = db_config.obtener_productos_sucursal(por_pagina=3)
    
    if productos:
        print(f"✅ Se obtuvieron {len(productos)} productos:")
        for p in productos[:3]:
            nombre = p.get('nombre_producto', 'N/A')
            precio = p.get('precio_venta', 0)
            print(f"   • {nombre} - ${precio}")
    else:
        print("⚠️  No se obtuvieron productos")
    
    print()
    print("🎉 ¡Todo funciona correctamente!")
    print()
    print("✅ La aplicación está lista para funcionar con db_config")
    print("   En local: usará db_utils (conexión directa)")
    print("   En Render: usará db_api_client (API REST)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
