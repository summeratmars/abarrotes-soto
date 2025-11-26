@echo off
cls
echo ========================================================
echo   CONFIGURACION COMPLETA - ABARROTES SOTO API REST
echo ========================================================
echo.
echo Este asistente te guiara por los pasos necesarios.
echo.
pause
echo.

echo [1/6] Verificando dependencias...
echo.
python -c "import fastapi, uvicorn, requests" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Faltan dependencias. Instalando...
    pip install -r requirements_api.txt
    if %errorlevel% neq 0 (
        echo ❌ Error al instalar dependencias.
        pause
        exit /b 1
    )
    echo ✅ Dependencias instaladas correctamente
) else (
    echo ✅ Dependencias ya instaladas
)
echo.
pause

echo [2/6] Verificando archivo .env...
echo.
if exist .env (
    echo ✅ Archivo .env encontrado
    findstr /C:"API_BASE_URL" .env >nul
    if %errorlevel% neq 0 (
        echo ⚠️  Agregando API_BASE_URL al .env...
        echo API_BASE_URL=http://localhost:8000 >> .env
        echo ✅ Variable agregada
    )
) else (
    echo ❌ No se encontro archivo .env
    echo    Asegurate de tener las credenciales de la base de datos
    pause
)
echo.
pause

echo [3/6] Iniciando API en segundo plano...
echo.
start /B python db_api_server.py
timeout /t 3 /nobreak >nul
echo ✅ API iniciada
echo.
pause

echo [4/6] Probando conexion a la API...
echo.
python test_api.py
if %errorlevel% neq 0 (
    echo ❌ Las pruebas fallaron. Revisa los errores arriba.
    pause
    exit /b 1
)
echo.
pause

echo [5/6] Informacion importante:
echo.
echo ✅ La API esta corriendo en: http://localhost:8001
echo 📚 Documentacion disponible en: http://localhost:8001/docs
echo.
echo Para que Render pueda acceder a tu API, necesitas:
echo.
echo   OPCION A - NGROK (Recomendado para pruebas):
echo   1. Descarga ngrok: https://ngrok.com/download
echo   2. Ejecuta: ngrok http 8001
echo   3. Copia la URL HTTPS que te da
echo   4. En Render, agrega variable: API_BASE_URL=https://tu-url.ngrok.io
echo.
echo   OPCION B - Port Forwarding (Produccion):
echo   1. Configura tu router para reenviar puerto 8001
echo   2. Obtén tu IP publica: https://www.whatismyip.com/
echo   3. En Render, agrega variable: API_BASE_URL=http://TU_IP:8001
echo.
pause

echo [6/6] Ultimo paso - Modificar app.py:
echo.
echo En tu archivo app.py, busca esta linea:
echo.
echo   from db_utils import get_db_connection, ...
echo.
echo Y reemplazala por:
echo.
echo   from db_config import get_db_connection, ...
echo.
echo Esto hara que tu app use automaticamente:
echo   - db_utils.py cuando corre en local
echo   - db_api_client.py cuando corre en Render
echo.
pause

echo.
echo ========================================================
echo   CONFIGURACION COMPLETADA
echo ========================================================
echo.
echo ✅ La API esta corriendo en tu PC
echo ✅ Las pruebas pasaron correctamente
echo.
echo PROXIMOS PASOS:
echo.
echo 1. Modifica app.py como se indico arriba
echo 2. Configura ngrok o port forwarding
echo 3. Agrega API_BASE_URL en Render
echo 4. Haz git push para desplegar
echo.
echo Lee MIGRACION_RAPIDA.md para mas detalles.
echo.
echo ========================================================
pause
