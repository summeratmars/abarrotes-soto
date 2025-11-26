# 🌐 API REST Local para Abarrotes Soto

Esta solución permite que tu aplicación Flask en Render acceda a la base de datos MySQL en tu PC local mediante una API REST, eliminando la necesidad de exponer directamente el puerto MySQL.

## 🏗️ Arquitectura

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Render.com    │         │    Tu PC Local   │         │   MySQL     │
│   (Flask App)   │────────▶│   API REST       │────────▶│  (Puerto    │
│                 │  HTTPS  │   (Puerto 8000)  │  Local  │   4407)     │
└─────────────────┘         └──────────────────┘         └─────────────┘
```

## 📁 Archivos Creados

1. **`db_api_server.py`** - Servidor API FastAPI que se ejecuta en tu PC local
2. **`db_api_client.py`** - Cliente que reemplaza `db_utils.py` para consumir la API
3. **`iniciar_api.bat`** - Script para iniciar fácilmente la API en Windows
4. **`requirements_api.txt`** - Dependencias necesarias para la API

## 🚀 Configuración Rápida

### 1. Instalar Dependencias de la API

En tu PC local, ejecuta:

```powershell
pip install fastapi uvicorn requests python-dotenv mysql-connector-python
```

O usa el archivo de requirements:

```powershell
pip install -r requirements_api.txt
```

### 2. Configurar Variables de Entorno

Asegúrate de que tu archivo `.env` tenga las credenciales de la base de datos:

```env
DB_HOST=localhost
DB_PORT=4407
DB_NAME=tu_base_datos
DB_USER=root
DB_PASSWORD=tu_contraseña

# Para desarrollo local:
API_BASE_URL=http://localhost:8000

# Para producción (Render), necesitarás exponer tu API:
# API_BASE_URL=https://tu-subdominio.ngrok.io
```

### 3. Iniciar la API Local

**Opción A - Usando el script bat:**
```powershell
.\iniciar_api.bat
```

**Opción B - Manual:**
```powershell
python db_api_server.py
```

La API se iniciará en `http://localhost:8000`

### 4. Verificar que la API Funciona

Abre en tu navegador: `http://localhost:8000`

Deberías ver:
```json
{
  "message": "API de Abarrotes Soto funcionando correctamente",
  "version": "1.0.0",
  "status": "online"
}
```

## 🌍 Exponer la API a Internet (Para Render)

Para que Render pueda acceder a tu API local, tienes 3 opciones:

### Opción 1: ngrok (Recomendado para pruebas)

1. Descarga ngrok: https://ngrok.com/download
2. Ejecuta:
   ```powershell
   ngrok http 8000
   ```
3. Copia la URL HTTPS que te da (ej: `https://abc123.ngrok.io`)
4. En Render, configura la variable de entorno:
   ```
   API_BASE_URL=https://abc123.ngrok.io
   ```

### Opción 2: Configurar Redirección de Puerto en Router

1. Accede a la configuración de tu router
2. Crea una regla de reenvío de puerto:
   - Puerto externo: 8000
   - Puerto interno: 8000
   - IP: La IP local de tu PC
3. Obtén tu IP pública en https://www.whatismyip.com/
4. En Render, configura:
   ```
   API_BASE_URL=http://TU_IP_PUBLICA:8000
   ```

### Opción 3: Servicio VPS/Cloud (Producción)

Considera migrar tu base de datos a un servicio cloud como:
- Railway (con MySQL)
- AWS RDS
- Google Cloud SQL
- DigitalOcean Managed Databases

## 🔄 Migración del Código Existente

### Para desarrollo local (no cambia nada):

Tu `app.py` sigue usando `db_utils.py` que se conecta directamente a MySQL.

### Para producción en Render:

**Cambio en `app.py`:**

```python
# Reemplaza esta línea:
from db_utils import get_db_connection, obtener_productos_sucursal, guardar_pedido_db, contar_productos_sucursal

# Por esta:
from db_api_client import get_db_connection, obtener_productos_sucursal, guardar_pedido_db, contar_productos_sucursal
```

¡Eso es todo! El resto del código sigue igual.

## 📋 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Verificar que la API está funcionando |
| GET | `/health` | Health check de API y base de datos |
| GET | `/api/productos` | Obtener productos con filtros |
| GET | `/api/productos/count` | Contar productos |
| GET | `/api/departamentos` | Listar departamentos |
| GET | `/api/categorias` | Listar categorías |
| POST | `/api/cotizacion` | Guardar cotización |
| POST | `/api/cliente/monedero` | Registrar cliente |
| GET | `/api/cliente/puntos` | Consultar puntos |
| POST | `/api/pedido` | Guardar pedido |

### Documentación Interactiva

Una vez que la API esté corriendo, puedes ver la documentación completa en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Probar la API

### Desde PowerShell:

```powershell
# Verificar health
Invoke-RestMethod -Uri http://localhost:8000/health

# Obtener productos
Invoke-RestMethod -Uri "http://localhost:8000/api/productos?departamento=ABARROTES"

# Obtener departamentos
Invoke-RestMethod -Uri http://localhost:8000/api/departamentos
```

### Desde Python:

```python
import requests

# Verificar conexión
response = requests.get("http://localhost:8000/health")
print(response.json())

# Obtener productos
response = requests.get("http://localhost:8000/api/productos", 
                        params={"departamento": "ABARROTES"})
products = response.json()["productos"]
print(f"Encontrados {len(products)} productos")
```

## 🔒 Seguridad

### Para Desarrollo Local:
- La API corre en localhost, no es accesible desde internet
- Las credenciales están en `.env` (no commitear a Git)

### Para Producción:
1. **Usa HTTPS** (ngrok lo provee automáticamente)
2. **Agrega autenticación** si es necesario:
   ```python
   from fastapi.security import HTTPBearer
   ```
3. **Restringe CORS** en `db_api_server.py`:
   ```python
   allow_origins=["https://tu-app.onrender.com"]
   ```
4. **Considera usar API Keys** para autenticar requests

## ⚙️ Variables de Entorno para Render

En tu proyecto de Render, configura:

```
API_BASE_URL=https://tu-api.ngrok.io
# o
API_BASE_URL=http://tu-ip-publica:8000
```

## 🐛 Troubleshooting

### Error: "No se pudo conectar con la API"
- Verifica que `db_api_server.py` está corriendo
- Revisa que el puerto 8000 no esté en uso
- Verifica la URL en `API_BASE_URL`

### Error: "Error de conexión a base de datos"
- Verifica las credenciales en `.env`
- Asegúrate que MySQL está corriendo en puerto 4407
- Revisa los logs de la API

### La API funciona local pero no desde Render
- Verifica que ngrok o el port forwarding está activo
- Confirma que `API_BASE_URL` en Render apunta a la URL correcta
- Revisa los logs de Render para ver el error específico

## 📊 Monitoreo

Para ver los logs de la API en tiempo real:

```powershell
# Los logs se muestran automáticamente en la consola donde corre uvicorn
```

## 🔄 Actualizaciones

Si actualizas el código de la API:

1. Detén el servidor (Ctrl+C)
2. Guarda los cambios en `db_api_server.py`
3. Reinicia: `python db_api_server.py`

No necesitas reiniciar la app en Render a menos que cambies `db_api_client.py`

## 💡 Mejoras Futuras

- [ ] Agregar caché con Redis para mejorar performance
- [ ] Implementar rate limiting para prevenir abuso
- [ ] Agregar autenticación con JWT tokens
- [ ] Logs estructurados con rotación
- [ ] Métricas con Prometheus
- [ ] Modo cluster para alta disponibilidad

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs de la API
2. Verifica las variables de entorno
3. Prueba los endpoints con `/docs`
4. Revisa que MySQL esté accesible

---

✅ **Todo listo!** Ahora tu tienda puede operar sin exponer directamente MySQL.
