#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from db_utils import obtener_productos_sucursal

def main():
    # Buscar productos con mayoreo
    productos = obtener_productos_sucursal()
    productos_mayoreo = [p for p in productos if p.get('precio_venta3', 0) > 0 and p.get('dCantMinPP3', 0) > 0]

    print(f'Productos con precio de mayoreo: {len(productos_mayoreo)}')
    print('=' * 50)
    
    for p in productos_mayoreo[:5]:  # Mostrar solo los primeros 5
        print(f'Nombre: {p["nombre_producto"]}')
        print(f'Código: {p["cbarras"]}')
        print(f'Precio normal: ${p["precio_venta"]}')
        print(f'Precio mayoreo: ${p["precio_venta3"]}') 
        print(f'Cantidad mínima mayoreo: {p["dCantMinPP3"]}')
        print(f'Ahorro por pieza: ${p["precio_venta"] - p["precio_venta3"]}')
        print('-' * 30)

if __name__ == "__main__":
    main()