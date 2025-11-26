# 📦 Solución Completa: API REST para Abarrotes Soto

## ✅ ¿Qué se ha creado?

Se ha desarrollado una **solución completa de API REST** para permitir que tu aplicación Flask en Render acceda a la base de datos MySQL local sin exponer directamente el puerto MySQL.

## 📁 Archivos Creados

| Archivo | Descripción |
|---------|-------------|
| `db_api_server.py` | ⭐ Servidor API FastAPI (corre en tu PC) |
| `db_api_client.py` | Cliente para consumir la API desde Render |
| `db_config.py` | Detecta automáticamente qué módulo usar |
| `requirements_api.txt` | Dependencias para la API |
| `iniciar_api.bat` | Script para iniciar la API fácilmente |
| `test_api.py` | Suite de pruebas para verificar la API |
| `API_README.md` | Documentación completa y detallada |
| `MIGRACION_RAPIDA.md` | Guía paso a paso de migración |

## 🚀 Inicio Rápido (5 minutos)

### 1. Instalar dependencias
```powershell
pip install -r requirements_api.txt
```

### 2. Iniciar la API en tu PC
```powershell
.\iniciar_api.bat
```

### 3. Probar que funciona
```powershell
python test_api.py
```

### 4. Modificar app.py

**Opción más fácil** - Reemplaza esta línea:
```python
from db_utils import get_db_connection, obtener_productos_sucursal, guardar_pedido_db, contar_productos_sucursal
```

Por esta:
```python
from db_config import get_db_connection, obtener_productos_sucursal, guardar_pedido_db, contar_productos_sucursal
```

**¡Eso es todo!** `db_config.py` detectará automáticamente:
- Si estás en local → usa `db_utils.py` (conexión directa)
- Si estás en Render → usa `db_api_client.py` (API REST)

### 5. Exponer la API a Internet

**Usando ngrok (recomendado):**
```powershell
ngrok http 8000
```
Copia la URL HTTPS que aparece.

### 6. Configurar Render

En las variables de entorno de Render, agrega:
```
API_BASE_URL=https://tu-url-ngrok.ngrok-free.app
```

### 7. Desplegar
```powershell
git add .
git commit -m "Implementar API REST"
git push
```

## 🎯 Arquitectura

```
┌─────────────────────┐
│   Render (Flask)    │
│                     │
│  ┌───────────────┐  │
│  │ db_config.py  │──┼──┐
│  └───────────────┘  │  │
│                     │  │  HTTPS
└─────────────────────┘  │
                         │
                         ▼
              ┌─────────────────────┐
              │    Tu PC Local      │
              │                     │
              │  ┌──────────────┐   │
              │  │ ngrok        │   │
              │  └──────┬───────┘   │
              │         │           │
              │  ┌──────▼───────┐   │
              │  │ API FastAPI  │   │
              │  │ (Puerto 8000)│   │
              │  └──────┬───────┘   │
              │         │           │
              │  ┌──────▼───────┐   │
              │  │ MySQL        │   │
              │  │ (Puerto 4407)│   │
              │  └──────────────┘   │
              └─────────────────────┘
```

## 🔍 Ventajas de esta Solución

✅ **No expones MySQL directamente** - Solo la API es accesible  
✅ **Código limpio** - Sin cambios masivos en app.py  
✅ **Detección automática** - Funciona en local y producción sin cambiar código  
✅ **Fácil de probar** - Suite de pruebas incluida  
✅ **Documentación completa** - Múltiples guías y ejemplos  
✅ **Escalable** - Puedes agregar más endpoints fácilmente  
✅ **Seguro** - CORS configurable, opción de autenticación  

## 📊 Endpoints Disponibles

| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Verificar API |
| `GET /health` | Health check |
| `GET /api/productos` | Listar productos |
| `GET /api/productos/count` | Contar productos |
| `GET /api/departamentos` | Listar departamentos |
| `GET /api/categorias` | Listar categorías |
| `POST /api/cotizacion` | Guardar cotización |
| `POST /api/cliente/monedero` | Registrar cliente |
| `GET /api/cliente/puntos` | Consultar puntos |
| `POST /api/pedido` | Guardar pedido |

Ver documentación interactiva: `http://localhost:8000/docs`

## 🧪 Validación

Después de configurar todo, verifica:

1. **API Local**: `http://localhost:8000` debe mostrar mensaje de bienvenida
2. **Health Check**: `http://localhost:8000/health` debe retornar `{"status": "healthy"}`
3. **Pruebas**: `python test_api.py` debe pasar todas las pruebas
4. **ngrok**: La URL de ngrok debe ser accesible desde internet
5. **Render**: Los logs deben mostrar `🌐 Modo: Producción - Usando API REST`

## 🔧 Comandos Útiles

```powershell
# Iniciar API
.\iniciar_api.bat

# O manualmente
python db_api_server.py

# Probar API
python test_api.py

# Ver documentación interactiva
start http://localhost:8000/docs

# Exponer con ngrok
ngrok http 8000

# Probar un endpoint específico
Invoke-RestMethod -Uri http://localhost:8000/health

# Ver productos
Invoke-RestMethod -Uri http://localhost:8000/api/productos | ConvertTo-Json
```

## 📚 Documentación

- **`API_README.md`** - Documentación técnica completa
- **`MIGRACION_RAPIDA.md`** - Guía paso a paso de migración
- **Este archivo** - Resumen ejecutivo

## ⚠️ Importante

### Para Producción:

1. **Mantén la API corriendo** - Necesitas dejar tu PC encendida con la API activa
2. **Mantén ngrok activo** - O configura port forwarding permanente
3. **Monitorea los logs** - Tanto de la API como de Render
4. **Configura CORS** - Restringe a tu dominio de Render

### Alternativa a Largo Plazo:

Considera migrar la base de datos a un servicio cloud:
- Railway MySQL
- PlanetScale
- AWS RDS
- Google Cloud SQL

Esto eliminaría la necesidad de mantener tu PC encendida 24/7.

## 🐛 Solución de Problemas

### Error: "No se pudo conectar con la API"
→ Verifica que la API esté corriendo y ngrok esté activo

### Error: "Error de conexión a base de datos"
→ Revisa las credenciales en `.env`

### La app funciona local pero no en Render
→ Verifica `API_BASE_URL` en las variables de entorno de Render

### ngrok se desconecta
→ Crea cuenta en ngrok.com para sesiones más largas

## 📞 Soporte

1. Lee `API_README.md` para documentación completa
2. Ejecuta `python test_api.py` para diagnóstico
3. Revisa los logs de la API y de Render
4. Verifica `/docs` para probar endpoints manualmente

## ✨ Próximos Pasos

Después de que todo funcione:

1. [ ] Configurar autenticación en la API
2. [ ] Restringir CORS a tu dominio
3. [ ] Agregar logging estructurado
4. [ ] Implementar rate limiting
5. [ ] Considerar migración de DB a cloud

---

**¿Todo listo?** Lee `MIGRACION_RAPIDA.md` para empezar 🚀
