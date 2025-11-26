# 🎯 Configuración de Variables de Entorno en Render

## Variable Requerida

En tu servicio de Render (https://dashboard.render.com), ve a:
**Environment** → **Environment Variables** → **Add Environment Variable**

### API_BASE_URL

**Descripción:** URL pública de tu API local

**Valor (elige uno):**

#### Opción A - Con ngrok:
```
https://TU-SUBDOMINIO.ngrok-free.app
```
Ejemplo: `https://abc123.ngrok-free.app`

#### Opción B - Con Port Forwarding (tu IP pública):
```
http://187.190.185.72:8001
```

⚠️ **IMPORTANTE:** 
- Si usas ngrok, usa la URL **HTTPS**
- Si usas port forwarding, usa **HTTP** (a menos que configures SSL)
- NO incluyas barra final (/)

---

## Pasos en Render:

1. Ve a: https://dashboard.render.com
2. Selecciona tu servicio web (abarrotes-soto)
3. Click en "Environment" en el menú lateral
4. Click en "Add Environment Variable"
5. Ingresa:
   - **Key:** `API_BASE_URL`
   - **Value:** (la URL de tu API)
6. Click en "Save Changes"
7. Render redesplegará automáticamente

---

## Verificar que funciona:

Después del redespliegue, revisa los logs de Render:

Deberías ver algo como:
```
🌐 [DB CONFIG] Modo: Producción - Usando API REST
🔗 [DB CONFIG] API URL: http://187.190.185.72:8001
```

Si ves errores de conexión, verifica que:
- Tu PC esté encendida
- La API esté corriendo (`python db_api_server.py`)
- La URL sea correcta
- (Si usas port forwarding) El firewall de Windows permita el puerto 8001

---

## 🔐 Variables Opcionales (para seguridad)

Si implementas API key (Paso 4), también agrega:

**API_KEY**
```
tu_clave_secreta_generada
```

Genera una clave segura con:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
