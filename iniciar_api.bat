@echo off
echo ============================================
echo   Iniciando API REST de Abarrotes Soto
echo ============================================
echo.
echo La API se iniciara en: http://localhost:8001
echo Documentacion disponible en: http://localhost:8001/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo ============================================
echo.

python db_api_server.py
