# 🚀 GUÍA DE DEPLOYMENT PARA RENDER# 🚀 DEPLOYMENT GUIDE - ABARROTES SOTO



## Resumen## 📋 Pre-requisitos

Esta aplicación es un sistema de eCommerce para Abarrotes Soto con integración a base de datos MariaDB, notificaciones por Telegram y sistema de monedero de puntos.

### 1. Base de Datos MariaDB/MySQL

## 🔧 Variables de entorno requeridas- Servidor de base de datos accesible desde internet

- Base de datos `puntoventa_db` configurada

### Obligatorias- Usuario con permisos de lectura/escritura

```bash

DB_HOST=tu_servidor_mariadb### 2. Bot de Telegram (opcional)

DB_USER=tu_usuario_db  - Bot creado en @BotFather

DB_PASSWORD=tu_password_db- Token del bot

DB_NAME=puntoventa_db- Chat ID para recibir notificaciones

DB_PORT=3306

FLASK_SECRET_KEY=genera_una_clave_unica_aqui## 🔧 Configuración en Render

```

### 1. Variables de Entorno **OBLIGATORIAS**

### Opcionales (Telegram)

```bash```bash

TELEGRAM_BOT_TOKEN=token_del_bot# Base de datos

TELEGRAM_CHAT_ID=id_del_chatDB_HOST=tu_servidor_mariadb.com

```DB_USER=tu_usuario

DB_PASSWORD=tu_password_seguro

## 📋 Configuración en RenderDB_NAME=puntoventa_db

DB_PORT=3306

1. **Conectar repositorio**: https://github.com/summeratmars/abarrotes-soto

2. **Configurar variables de entorno** en el dashboard de Render# Flask

3. **Deployment automático** se activará con cada push a mainFLASK_SECRET_KEY=genera_una_clave_unica_y_segura_aqui

```

## ✅ Funcionalidades

### 2. Variables de Entorno **OPCIONALES** para Telegram

- ✅ Tienda en línea responsiva

- ✅ Sistema de carrito de compras  ```bash

- ✅ Integración con base de datos MariaDBTELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

- ✅ Sistema de monedero de puntosTELEGRAM_CHAT_ID=123456789

- ✅ Notificaciones por Telegram```

- ✅ Panel de administración

- ✅ Gestión de productos e imágenes## 📚 Pasos de Deployment



## 🛡️ Seguridad### Opción A: Deployment Automático desde GitHub



- ✅ Variables de entorno para credenciales1. **Conectar Repository a Render:**

- ✅ Archivos sensibles en .gitignore   ```

- ✅ Sin credenciales hardcodeadas   - Ve a https://render.com

- ✅ Protección contra secretos en GitHub   - Crea nuevo Web Service
   - Conecta tu repositorio GitHub
   - Branch: main
   ```

2. **Configurar Build Settings:**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   Environment: Python 3.11.9
   ```

3. **Añadir Variables de Entorno:**
   - En el dashboard de Render
   - Environment → Add Environment Variable
   - Añadir todas las variables listadas arriba

### Opción B: Deploy Manual usando render.yaml

El archivo `render.yaml` ya está configurado. Solo necesitas:

1. Hacer push a GitHub
2. En Render, usar "Deploy from GitHub"
3. Configurar las variables de entorno

## 🔐 Seguridad

### Variables que NUNCA deben estar en el código:
- ❌ Credenciales de base de datos
- ❌ Tokens de API
- ❌ Claves secretas
- ❌ Contraseñas

### Variables que SÍ pueden estar en el código:
- ✅ Configuraciones por defecto
- ✅ URLs públicas
- ✅ Nombres de archivos
- ✅ Configuraciones de UI

## 🧪 Testing de Deployment

### 1. Verificar Variables de Entorno
```bash
# En el dashboard de Render, verificar que todas las variables estén configuradas
```

### 2. Verificar Conexión a Base de Datos
```bash
# La app debe conectarse sin errores al arrancar
# Revisar logs en Render dashboard
```

### 3. Verificar Funcionalidades
- [ ] Página principal carga
- [ ] Catálogo de productos se muestra
- [ ] Carrito funciona
- [ ] Sistema de cotizaciones funciona
- [ ] Notificaciones de Telegram (si configuradas)

## 🚨 Troubleshooting

### Error: "can't connect to MySQL server"
```bash
# Verificar:
1. DB_HOST es accesible desde internet
2. DB_PORT correcto (normalmente 3306)
3. Credenciales DB_USER y DB_PASSWORD correctas
4. Base de datos DB_NAME existe
```

### Error: "Application failed to start"
```bash
# Revisar logs en Render dashboard
# Verificar que todas las variables de entorno obligatorias estén configuradas
```

### Error: "Internal Server Error"
```bash
# Revisar logs de la aplicación
# Verificar que las tablas de la base de datos existan
# Verificar permisos del usuario de base de datos
```

## 📊 Monitoreo

### Logs de Aplicación
- Disponibles en Render Dashboard → Logs
- Filtrar por errores para debugging

### Notificaciones de Productos sin Imagen
- Si Telegram está configurado, recibirás notificaciones automáticas
- Revisar endpoint `/api/imagenes/estadisticas` para métricas

## 🔄 Actualizaciones

### Para actualizar el código:
1. Hacer push a la rama `main` en GitHub
2. Render detectará automáticamente el cambio
3. Se ejecutará build y deploy automático

### Para actualizar variables de entorno:
1. Ir a Render Dashboard → Environment
2. Modificar/añadir variables
3. La aplicación se reiniciará automáticamente

## 📝 Notas Importantes

- **Backup de Base de Datos:** Siempre hacer backup antes de deployment
- **SSL/HTTPS:** Render proporciona HTTPS automáticamente
- **Dominio:** Render asigna un dominio automático, puedes configurar uno personalizado
- **Escalamiento:** La app está optimizada para deployment básico

## 🆘 Soporte

Si encuentras problemas:
1. Revisar este README
2. Verificar logs en Render dashboard
3. Verificar configuración de variables de entorno
4. Contactar al equipo de desarrollo
