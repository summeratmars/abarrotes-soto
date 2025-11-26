# 🌐 Instrucciones para Exponer la API con ngrok

## Paso 1: Descargar ngrok

1. Ve a: https://ngrok.com/download
2. Descarga la versión para Windows
3. Descomprime el archivo `ngrok.exe` en una carpeta (por ejemplo: `C:\ngrok\`)

## Paso 2: (Opcional) Crear cuenta en ngrok

Para sesiones más largas y estables:
1. Ve a: https://dashboard.ngrok.com/signup
2. Crea una cuenta gratuita
3. Copia tu authtoken desde: https://dashboard.ngrok.com/get-started/your-authtoken
4. Ejecuta en PowerShell:
   ```powershell
   C:\ngrok\ngrok.exe authtoken TU_TOKEN_AQUI
   ```

## Paso 3: Ejecutar ngrok

**IMPORTANTE:** Asegúrate de que tu API esté corriendo en otra terminal:
```powershell
python db_api_server.py
```

Luego, en una **nueva terminal**, ejecuta:

```powershell
# Si ngrok.exe está en C:\ngrok\
C:\ngrok\ngrok.exe http 8001

# O si lo agregaste al PATH:
ngrok http 8001
```

## Paso 4: Copiar la URL

Verás algo como esto:

```
ngrok

Session Status                online
Account                       tu_cuenta (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8001

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Copia la URL HTTPS** (ejemplo: `https://abc123.ngrok-free.app`)

## Paso 5: Probar la URL

En otra terminal de PowerShell, prueba que funcione:

```powershell
Invoke-RestMethod -Uri "https://TU-URL-NGROK.ngrok-free.app/health"
```

Deberías ver:
```
status   database
------   --------
healthy  connected
```

## Paso 6: Guardar la URL

Guarda esta URL porque la necesitarás para:
1. Configurar la variable `API_BASE_URL` en Render
2. Actualizar el `.env` local si quieres probar el modo producción

---

## 🔄 Alternativa: Port Forwarding

Si no quieres usar ngrok, puedes configurar port forwarding en tu router:

1. Accede a tu router (usualmente `192.168.1.1` o `192.168.0.1`)
2. Busca la sección "Port Forwarding" o "Reenvío de Puertos"
3. Crea una nueva regla:
   - Puerto externo: `8001`
   - Puerto interno: `8001`
   - IP destino: Tu IP local (obtenerla con `ipconfig`)
   - Protocolo: TCP
4. Obtén tu IP pública: https://www.whatismyip.com/
5. Tu API estará en: `http://TU_IP_PUBLICA:8001`

**⚠️ Advertencia:** Port forwarding expone tu PC directamente a internet. Asegúrate de implementar seguridad (API key, firewall).

---

## ✅ Siguiente Paso

Una vez que tengas la URL de ngrok funcionando, continúa con:
**Paso 3: Configurar API_BASE_URL en Render**
