"""
Script para aplicar automáticamente los cambios de db_utils a db_config
en app.py y routes.py
"""

import os
import re
import shutil
from datetime import datetime

def hacer_backup(archivo):
    """Crear backup del archivo antes de modificarlo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = f"{archivo}.backup_{timestamp}"
    shutil.copy2(archivo, backup)
    print(f"✅ Backup creado: {backup}")
    return backup

def aplicar_cambios(archivo, cambios_realizados):
    """Aplicar cambios en un archivo"""
    if not os.path.exists(archivo):
        print(f"⚠️  Archivo no encontrado: {archivo}")
        return False
    
    print(f"\n📝 Procesando: {archivo}")
    
    # Leer contenido
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    
    # Aplicar reemplazos
    # Patrón: from db_utils import ...
    patron = r'from\s+db_utils\s+import\s+'
    reemplazo = 'from db_config import '
    
    contenido_modificado, n_cambios = re.subn(patron, reemplazo, contenido)
    
    if n_cambios > 0:
        # Crear backup
        backup = hacer_backup(archivo)
        
        # Guardar cambios
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido_modificado)
        
        print(f"✅ Se realizaron {n_cambios} cambio(s) en {archivo}")
        cambios_realizados[archivo] = n_cambios
        return True
    else:
        print(f"ℹ️  No se encontraron cambios necesarios en {archivo}")
        return False

def eliminar_obtener_cliente_por_telefono(archivo):
    """Eliminar la función obtener_cliente_por_telefono del import de routes.py"""
    if not os.path.exists(archivo):
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar y eliminar obtener_cliente_por_telefono
    patron = r',\s*obtener_cliente_por_telefono'
    contenido_modificado = re.sub(patron, '', contenido)
    
    if contenido != contenido_modificado:
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido_modificado)
        print(f"ℹ️  Eliminada función inexistente 'obtener_cliente_por_telefono' de {archivo}")
        return True
    
    return False

def main():
    print("=" * 70)
    print("  MIGRACIÓN AUTOMÁTICA A API REST")
    print("=" * 70)
    print()
    print("Este script cambiará automáticamente los imports de:")
    print("  from db_utils import ... → from db_config import ...")
    print()
    print("Archivos a modificar:")
    print("  - app.py")
    print("  - routes.py")
    print()
    
    respuesta = input("¿Deseas continuar? (s/n): ").strip().lower()
    if respuesta not in ['s', 'si', 'y', 'yes']:
        print("\n❌ Operación cancelada por el usuario")
        return
    
    print("\n" + "=" * 70)
    print("  INICIANDO MIGRACIÓN")
    print("=" * 70)
    
    cambios_realizados = {}
    
    # Aplicar cambios en app.py
    aplicar_cambios('app.py', cambios_realizados)
    
    # Aplicar cambios en routes.py
    if aplicar_cambios('routes.py', cambios_realizados):
        # Eliminar obtener_cliente_por_telefono si existe
        eliminar_obtener_cliente_por_telefono('routes.py')
    
    print("\n" + "=" * 70)
    print("  RESUMEN")
    print("=" * 70)
    
    if cambios_realizados:
        print("\n✅ Cambios aplicados exitosamente:")
        for archivo, n_cambios in cambios_realizados.items():
            print(f"   • {archivo}: {n_cambios} cambio(s)")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Revisa los archivos modificados")
        print("   2. Prueba la aplicación localmente:")
        print("      python app.py")
        print("   3. Si todo funciona, haz commit:")
        print("      git add app.py routes.py")
        print('      git commit -m "Migrar a API REST"')
        print("      git push")
        print("\n💡 Los backups están guardados por si necesitas revertir")
    else:
        print("\nℹ️  No se realizaron cambios (¿ya estaban aplicados?)")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
