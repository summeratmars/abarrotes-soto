# 🚀 Configuración Base de Datos Railway + Despliegue en Render

## ✅ PASO 1: Archivo .env Ya Actualizado

Tu archivo `.env` local ya está configurado con las credenciales de Railway:

```env
DB_HOST=caboose.proxy.rlwy.net
DB_PORT=18465
DB_NAME=railway
DB_USER=root
DB_PASSWORD=lXylQBJYgXDPFeEyRGYmWpahSLTfoXxe
```

## 📋 PASO 2: Configurar Variables de Entorno en Render

Ve a tu proyecto en Render (https://dashboard.render.com) y configura las siguientes **Variables de Entorno**:

### 🔧 Variables de Base de Datos Railway:

```
DB_HOST = caboose.proxy.rlwy.net
DB_PORT = 18465
DB_NAME = railway
DB_USER = root
DB_PASSWORD = lXylQBJYgXDPFeEyRGYmWpahSLTfoXxe
```

### 🔐 Variables de Flask (IMPORTANTES):

```
FLASK_SECRET_KEY = [genera_una_clave_secreta_aqui]
ADMIN_PASSWORD = [tu_password_admin]
MANAGER_PASSWORD = [tu_password_manager]
```

### 📱 Variables de Telegram (ya tienes):

```
TELEGRAM_BOT_TOKEN = 8109281070:AAGVzQEv2YKfbF6giG33-GdJPHWKTHSBDQ8
TELEGRAM_CHAT_ID = 7799086527
```

### 📧 Variables de Gmail (ya tienes):

```
GMAIL_USER = sotojaimes98@gmail.com
GMAIL_APP_PASSWORD = peev aiuu kevv qpqe
```

## 🎯 PASO 3: Cómo Agregar Variables en Render

1. **Ingresa a Render**: https://dashboard.render.com
2. **Selecciona tu servicio** (abarrotes-soto)
3. **Ve a "Environment"** en el menú lateral
4. **Click en "Add Environment Variable"**
5. **Agrega cada variable** una por una:
   - Key: `DB_HOST`
   - Value: `caboose.proxy.rlwy.net`
   - Click "Save Changes"
6. **Repite** para todas las variables listadas arriba

## 🔄 PASO 4: Redesplegar tu Aplicación

Después de agregar las variables de entorno:

1. Ve a la sección **"Manual Deploy"**
2. Click en **"Deploy latest commit"**
3. Espera a que termine el despliegue (puede tardar 2-5 minutos)

## ✨ PASO 5: Verificar la Conexión

Una vez desplegado, tu aplicación:

- ✅ Se conectará automáticamente a Railway
- ✅ Usará la base de datos en la nube
- ✅ Todos los productos y datos estarán sincronizados

## 📸 Captura de Pantalla de Ejemplo

En Render, tus variables deberían verse así:

```
Environment Variables:
├── DB_HOST: caboose.proxy.rlwy.net
├── DB_PORT: 18465
├── DB_NAME: railway
├── DB_USER: root
├── DB_PASSWORD: lXylQBJYgXDPFeEyRGYmWpahSLTfoXxe
├── FLASK_SECRET_KEY: [tu_clave_secreta]
├── ADMIN_PASSWORD: [tu_password]
├── TELEGRAM_BOT_TOKEN: 8109281070:AAG...
└── TELEGRAM_CHAT_ID: 7799086527
```

## ⚠️ IMPORTANTE: Generar Flask Secret Key

Para generar una clave secreta segura, ejecuta en tu terminal:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Usa el resultado como tu `FLASK_SECRET_KEY` en Render.

## 🔧 Troubleshooting

### Error: "Can't connect to MySQL server"
- ✅ Verifica que todas las variables estén exactamente como se muestra
- ✅ Revisa que `DB_PORT` sea `18465` (número, no texto)
- ✅ Confirma que Railway esté activo

### Error: "Access denied for user"
- ✅ Verifica que `DB_PASSWORD` sea exacta (sin espacios extras)
- ✅ Confirma que `DB_USER` sea `root`

### La aplicación no se conecta
- ✅ Haz un nuevo deploy manual en Render
- ✅ Revisa los logs en Render para ver errores específicos

## 📞 Contacto

Si tienes problemas, revisa los logs en:
- Render: Dashboard > Tu servicio > Logs
- Railway: Dashboard > Tu base de datos > Logs

---

**Fecha de configuración**: 5 de noviembre de 2025
**Base de datos**: Railway MySQL
**Hosting**: Render
