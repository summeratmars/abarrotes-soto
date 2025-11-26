# 🚀 Guía Rápida: Migración a API REST

## Para Uso Local (Sin cambios)

Tu aplicación sigue funcionando igual. No necesitas hacer nada.

## Para Producción en Render

### Paso 1: Preparar tu PC Local

```powershell
# Instalar dependencias
pip install -r requirements_api.txt

# Iniciar la API
.\iniciar_api.bat

# O manualmente:
python db_api_server.py
```

La API debería estar corriendo en `http://localhost:8000`

### Paso 2: Probar la API Localmente

```powershell
# Ejecutar pruebas
python test_api.py
```

Si todas las pruebas pasan ✅, continúa al siguiente paso.

### Paso 3: Exponer la API a Internet

#### Opción A: Usar ngrok (Más fácil)

1. Descarga ngrok: https://ngrok.com/download
2. Descomprime y ejecuta:
   ```powershell
   .\ngrok.exe http 8000
   ```
3. Copia la URL HTTPS que aparece (ej: `https://abc123.ngrok-free.app`)
4. **IMPORTANTE**: Mantén ngrok corriendo mientras tu app esté en producción

#### Opción B: Port Forwarding en Router

1. Accede a tu router (usualmente `192.168.1.1`)
2. Busca "Port Forwarding" o "Reenvío de Puertos"
3. Crea regla:
   - Puerto externo: `8000`
   - Puerto interno: `8000`
   - IP local de tu PC: (encuéntrala con `ipconfig`)
4. Obtén tu IP pública: https://www.whatismyip.com/
5. Tu API estará en: `http://TU_IP_PUBLICA:8000`

### Paso 4: Modificar app.py para Producción

**Opción A - Detección Automática (Recomendado):**

Agrega esto al inicio de `app.py`:

```python
import os

# Detectar entorno
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER'):
    # En producción, usar API
    from db_api_client import (
        get_db_connection, 
        obtener_productos_sucursal, 
        guardar_pedido_db, 
        contar_productos_sucursal,
        guardar_cotizacion_web,
        registrar_cliente_monedero
    )
    print("🌐 Modo: Producción (usando API REST)")
else:
    # En local, conexión directa
    from db_utils import (
        get_db_connection, 
        obtener_productos_sucursal, 
        guardar_pedido_db, 
        contar_productos_sucursal,
        guardar_cotizacion_web,
        registrar_cliente_monedero
    )
    print("💻 Modo: Local (conexión directa)")
```

**Opción B - Manual:**

Reemplaza esta línea en `app.py`:
```python
# ANTES:
from db_utils import get_db_connection, obtener_productos_sucursal, guardar_pedido_db, contar_productos_sucursal

# DESPUÉS:
from db_api_client import get_db_connection, obtener_productos_sucursal, guardar_pedido_db, contar_productos_sucursal
```

### Paso 5: Configurar Variable de Entorno en Render

1. Ve a tu proyecto en Render.com
2. Ve a "Environment" > "Environment Variables"
3. Agrega nueva variable:
   ```
   Key: API_BASE_URL
   Value: https://tu-url-ngrok.ngrok-free.app
   ```
   (O tu URL de port forwarding: `http://TU_IP_PUBLICA:8000`)
4. Guarda cambios
5. Render redesplegará automáticamente

### Paso 6: Actualizar requirements.txt de Render

Agrega al final de `requirements.txt`:

```
requests>=2.31.0
```

Esto es necesario para que `db_api_client.py` funcione en Render.

### Paso 7: Desplegar y Probar

1. Commit y push a Git:
   ```powershell
   git add .
   git commit -m "Migrar a API REST"
   git push
   ```

2. Render desplegará automáticamente

3. Verifica los logs en Render:
   - Busca: `🌐 Modo: Producción (usando API REST)`
   - Si hay errores de conexión, revisa que la API esté accesible

### Paso 8: Verificar Funcionamiento

1. Abre tu tienda en Render
2. Navega por productos
3. Agrega algo al carrito
4. Realiza una compra de prueba

Si todo funciona, ¡listo! 🎉

## 🔧 Troubleshooting

### Error: "No se pudo conectar con la API"

**Causa**: Render no puede acceder a tu API local

**Solución**:
1. Verifica que la API esté corriendo en tu PC
2. Verifica que ngrok esté activo
3. Verifica que `API_BASE_URL` en Render sea correcta
4. Prueba la URL manualmente en tu navegador

### Error: "Error de conexión a base de datos"

**Causa**: La API no puede conectar con MySQL

**Solución**:
1. Verifica credenciales en `.env`
2. Verifica que MySQL esté corriendo
3. Revisa los logs de la API

### La API funciona local pero no desde Render

**Causa**: Firewall o configuración de red

**Solución**:
1. Desactiva temporalmente el firewall de Windows
2. Verifica reglas de port forwarding en router
3. Usa ngrok como alternativa

### ngrok se desconecta frecuentemente

**Causa**: Plan gratuito de ngrok

**Solución**:
1. Crea cuenta en ngrok.com para sesiones más largas
2. Considera actualizar a plan de pago
3. Usa port forwarding como alternativa

## 📊 Monitoreo

### Ver logs de la API:

Los logs aparecen automáticamente en la consola donde corre `db_api_server.py`

### Ver logs de Render:

1. Ve a tu proyecto en Render
2. Click en "Logs"
3. Busca mensajes de error

## 🔒 Seguridad para Producción

### 1. Restringe CORS

En `db_api_server.py`, cambia:

```python
allow_origins=["*"]  # ❌ No seguro

# Por:
allow_origins=["https://tu-app.onrender.com"]  # ✅ Seguro
```

### 2. Agrega Autenticación (Opcional)

```python
from fastapi import Header, HTTPException

API_KEY = os.environ.get('API_KEY', 'tu-clave-secreta')

async def verify_token(x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="No autorizado")
```

### 3. Usa HTTPS

- ngrok lo provee automáticamente ✅
- Port forwarding necesita configuración adicional con certificados SSL

## 💰 Costos

- **ngrok gratuito**: Suficiente para pruebas, se desconecta periódicamente
- **ngrok Pro**: ~$8/mes, conexiones estables
- **Migrar DB a cloud**: Variable según proveedor (Railway, AWS RDS, etc.)

## 🎯 Siguiente Paso Recomendado

Para una solución más robusta, considera migrar la base de datos a:

1. **Railway MySQL** (incluye plan gratuito)
2. **PlanetScale** (MySQL serverless)
3. **Supabase** (PostgreSQL con extras)

Esto eliminaría la necesidad de mantener tu PC encendida 24/7.

---

¿Necesitas ayuda? Revisa `API_README.md` para documentación completa.
