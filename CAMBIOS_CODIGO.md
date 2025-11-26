# 🔧 Modificación Exacta para app.py

## ⚠️ Cambio Requerido

Para que tu aplicación use automáticamente la API cuando esté en Render y la conexión directa cuando esté en local, necesitas hacer UN SOLO CAMBIO:

## 📝 Ubicación del Cambio

Archivo: `app.py`  
Línea: ~11 (cerca del inicio, después de los imports de Flask)

## 🔴 ANTES (Línea actual):

```python
from db_utils import get_db_connection, obtener_productos_sucursal, guardar_pedido_db, contar_productos_sucursal, contar_productos_sucursal
```

## 🟢 DESPUÉS (Nueva línea):

```python
from db_config import get_db_connection, obtener_productos_sucursal, guardar_pedido_db, contar_productos_sucursal, contar_productos_sucursal
```

**Solo cambias `db_utils` por `db_config`**

---

## ✅ Eso es TODO en app.py

Sin embargo, hay otras 2 líneas en `app.py` que también importan de `db_utils` dinámicamente. Debes cambiarlas también:

### Cambio 2 - Línea ~223:

**ANTES:**
```python
from db_utils import guardar_cotizacion_web
```

**DESPUÉS:**
```python
from db_config import guardar_cotizacion_web
```

### Cambio 3 - Línea ~243:

**ANTES:**
```python
from db_utils import registrar_cliente_monedero
```

**DESPUÉS:**
```python
from db_config import registrar_cliente_monedero
```

### Cambio 4 - Línea ~918:

**ANTES:**
```python
from db_utils import get_db_connection
```

**DESPUÉS:**
```python
from db_config import get_db_connection
```

---

## 📄 También en routes.py

Archivo: `routes.py`  
Línea: ~4

**ANTES:**
```python
from db_utils import obtener_productos_sucursal, guardar_cotizacion_web, registrar_cliente_monedero, obtener_cliente_por_telefono, contar_productos_sucursal
```

**DESPUÉS:**
```python
from db_config import obtener_productos_sucursal, guardar_cotizacion_web, registrar_cliente_monedero, contar_productos_sucursal
```

⚠️ **NOTA**: Eliminé `obtener_cliente_por_telefono` porque esa función no existe en `db_utils.py`. Si la necesitas, avísame para agregarla a la API.

---

## 🧪 Verificación

Después de hacer estos cambios, verifica:

### 1. En Local (debe seguir funcionando igual):

```powershell
python app.py
```

Deberías ver en consola:
```
💻 [DB CONFIG] Modo: Local - Conexión directa a MySQL
```

### 2. Simulando Producción:

```powershell
$env:RENDER="true"
python app.py
```

Deberías ver:
```
🌐 [DB CONFIG] Modo: Producción - Usando API REST
🔗 [DB CONFIG] API URL: http://localhost:8000
```

---

## 🎯 ¿Por qué funciona?

El archivo `db_config.py` que creamos:

1. **Detecta automáticamente** el entorno (local vs Render)
2. **Importa el módulo correcto**:
   - Local → `db_utils.py` (conexión directa)
   - Render → `db_api_client.py` (consume API)
3. **Exporta las mismas funciones** para mantener compatibilidad

## 💡 Beneficios

✅ **Un solo cambio** - Solo modificas el import  
✅ **Automático** - No necesitas código condicional en app.py  
✅ **Compatible** - El resto del código sigue igual  
✅ **Reversible** - Puedes volver fácilmente al anterior  

---

## 🔄 Resumen de Todos los Cambios

### Archivos a Modificar:

1. **app.py** - 4 cambios (líneas ~11, ~223, ~243, ~918)
2. **routes.py** - 1 cambio (línea ~4)

### Patrón del Cambio:

```python
# Buscar todas las líneas que digan:
from db_utils import ...

# Reemplazar por:
from db_config import ...
```

---

## 🚀 Después de los Cambios

1. **Commit** los cambios:
   ```powershell
   git add app.py routes.py
   git commit -m "Migrar a API REST con db_config"
   ```

2. **Probar localmente**:
   ```powershell
   python app.py
   # Verificar que funcione normal
   ```

3. **Push a Git**:
   ```powershell
   git push
   ```

4. **Render desplegará automáticamente** y usará la API 🎉

---

## ⚠️ Importante

- **No elimines `db_utils.py`** - Se necesita para desarrollo local
- **No elimines `db_api_client.py`** - Se necesita para Render
- **`db_config.py` decide cuál usar** automáticamente

---

¿Dudas? Lee `MIGRACION_RAPIDA.md` o `SOLUCION_API_REST.md`
