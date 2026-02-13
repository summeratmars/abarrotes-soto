"""Test rápido de conexión a azula_pdv"""
import sys
sys.path.insert(0, '.')

from db_utils import get_db_connection, obtener_productos_sucursal, obtener_departamentos, obtener_categorias, contar_productos_sucursal

# Test conexión
conn = get_db_connection()
print('✅ Conexión OK:', conn.is_connected())
conn.close()

# Test departamentos
deps = obtener_departamentos()
print(f'\n📦 Departamentos ({len(deps)}):')
for d in deps:
    print(f'  - {d}')

# Test categorías
cats = obtener_categorias('Abarrotes')
print(f'\n📁 Categorías de Abarrotes ({len(cats)}):')
for c in cats:
    print(f'  - {c}')

# Test productos
total = contar_productos_sucursal()
print(f'\n📊 Total productos con stock: {total}')

prods = obtener_productos_sucursal(por_pagina=5)
print(f'\n🛒 Primeros 5 productos:')
for p in prods:
    print(f'  {p["cbarras"]} | {p["nombre_producto"]} | ${p["precio_venta"]:.2f} | PV2: ${p["precio_venta2"]:.2f} | Stock: {p["existencia"]}')

# Test ofertas
ofertas = obtener_productos_sucursal(categoria='ofertas', por_pagina=3)
print(f'\n🏷️ Ofertas ({len(ofertas)} primeras):')
for p in ofertas:
    print(f'  {p["nombre_producto"]} | Normal: ${p["precio_venta"]:.2f} | Oferta: ${p["precio_venta2"]:.2f}')

print('\n✅ Todas las pruebas pasaron correctamente!')
